import numpy as np

from fastapi import HTTPException
from sqlmodel import Session
from sklearn.manifold import TSNE

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings

from app.core.config import Config
from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.models.embeddings import (
    EmbeddingsGetRequest,
    EmbeddingsGetResponse,
    EmbeddingsReduceRequest,
    EmbeddingsReduceResponse,
    EmbeddingsSimilaritiesRequest,
    EmbeddingsSimilaritiesResponse,
)


class EmbeddingsService:
    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @log_decorator
    def get(self, request: EmbeddingsGetRequest) -> EmbeddingsGetResponse:
        llm_service = LLMService(db_session=self.db_session)
        llm = llm_service.get_by_id(id=request.llm_id)

        if not llm:
            raise HTTPException(status_code=404, detail=f"LLM {request.llm_id} not found")

        if llm.provider == "openai":
            embeddings = OpenAIEmbeddings(
                model=llm.name,
                base_url=Config.OPENAI_API_ENDPOINT,
                openai_api_key=Config.OPENAI_API_KEY,
            )
        elif llm.provider == "ollama":
            embeddings = OllamaEmbeddings(
                model=llm.name, base_url=Config.OLLAMA_API_ENDPOINT
            )
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Provider {llm.provider} does not support embeddings",
            )

        return EmbeddingsGetResponse(
            embeddings=embeddings.embed_documents(request.texts)
        )

    @log_decorator
    def similarities(
        self, request: EmbeddingsSimilaritiesRequest
    ) -> EmbeddingsSimilaritiesResponse:
        if not request.embeddings:
            raise HTTPException(status_code=422, detail="embeddings must not be empty")
        E = np.array(request.embeddings)
        M = E / np.linalg.norm(E, axis=1, keepdims=True)
        Q = M[0]
        S = M @ Q

        return EmbeddingsSimilaritiesResponse(similarities=S.tolist())

    @log_decorator
    def reduce(self, request: EmbeddingsReduceRequest) -> EmbeddingsReduceResponse:
        if request.target_dims not in (2, 3):
            raise HTTPException(
                status_code=422, detail="Target dimensions must be either 2 or 3"
            )

        # t-SNE needs perplexity strictly less than the number of samples; the
        # previous `len(embeddings) - 1` would degenerate to 0 for a single
        # input and crash sklearn with a confusing message.
        n_samples = len(request.embeddings)
        if n_samples < 3:
            raise HTTPException(
                status_code=422,
                detail="at least 3 embeddings are required for t-SNE reduction",
            )
        perplexity = min(30, n_samples - 1)

        tsne = TSNE(
            n_iter=1000,
            random_state=42,
            learning_rate=200,
            n_components=request.target_dims,
            perplexity=perplexity,
        )

        reduced_embeddings = tsne.fit_transform(np.array(request.embeddings))

        return EmbeddingsReduceResponse(
            reduced_embeddings=reduced_embeddings.tolist()
        )
