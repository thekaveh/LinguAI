from typing import List
from sqlmodel import SQLModel, Field


class EmbeddingsGetRequest(SQLModel, table=False):
    llm_id: int = Field(nullable=False)
    texts: List[str] = Field(nullable=False)


class EmbeddingsGetResponse(SQLModel, table=False):
    embeddings: List[List[float]] = Field(nullable=False)


class EmbeddingsSimilaritiesRequest(SQLModel, table=False):
    embeddings: List[List[float]] = Field(nullable=False)


class EmbeddingsSimilaritiesResponse(SQLModel, table=False):
    similarities: List[float] = Field(nullable=False)


class EmbeddingsReduceRequest(SQLModel, table=False):
    embeddings: List[List[float]] = Field(nullable=False)
    target_dims: int = Field(nullable=False)


class EmbeddingsReduceResponse(SQLModel, table=False):
    reduced_embeddings: List[List[float]] = Field(nullable=False)
