import numpy as np

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
        try:
            llm_service = LLMService(db_session=self.db_session)
            llm = llm_service.get_by_id(id=request.llm_id)

            if not llm:
                raise Exception(f"Model {request.model} not found!")

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
                raise Exception(f"Provider {llm.provider} not supported!")

            return EmbeddingsGetResponse(
                embeddings=embeddings.embed_documents(request.texts)
            )
        except Exception as e:
            raise e

    @log_decorator
    def similarities(
        self, request: EmbeddingsSimilaritiesRequest
    ) -> EmbeddingsSimilaritiesResponse:
        try:
            E = np.array(request.embeddings)
            M = E / np.linalg.norm(E, axis=1, keepdims=True)
            Q = M[0]
            S = M @ Q

            return EmbeddingsSimilaritiesResponse(similarities=S.tolist())
        except Exception as e:
            raise e

    @log_decorator
    def reduce(self, request: EmbeddingsReduceRequest) -> EmbeddingsReduceResponse:
        try:
            if request.target_dims <= 1 or request.target_dims >= 4:
                raise Exception("Target dimensions must be either 2 or 3!")

            tsne = TSNE(
                n_iter=1000,
                random_state=42,
                learning_rate=200,
                n_components=request.target_dims,
                perplexity=len(request.embeddings) - 1,
            )

            reduced_embeddings = tsne.fit_transform(np.array(request.embeddings))

            return EmbeddingsReduceResponse(
                reduced_embeddings=reduced_embeddings.tolist()
            )
        except Exception as e:
            raise e
