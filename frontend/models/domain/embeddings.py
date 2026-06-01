from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field


class EmbeddingsGetRequest(BaseModel):
    llm_id: int = Field(...)
    texts: List[str] = Field(...)


class EmbeddingsGetResponse(BaseModel):
    embeddings: List[List[float]] = Field(...)


class EmbeddingsSimilaritiesRequest(BaseModel):
    embeddings: List[List[float]] = Field(...)


class EmbeddingsSimilaritiesResponse(BaseModel):
    similarities: List[float] = Field(...)


class EmbeddingsReduceRequest(BaseModel):
    embeddings: List[List[float]] = Field(...)
    target_dims: int = Field(...)


class EmbeddingsReduceResponse(BaseModel):
    reduced_embeddings: List[List[float]] = Field(...)
