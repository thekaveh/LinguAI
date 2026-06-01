from __future__ import annotations
import httpx

from models.domain.embeddings import (
    EmbeddingsGetRequest, EmbeddingsGetResponse,
    EmbeddingsReduceRequest, EmbeddingsReduceResponse,
    EmbeddingsSimilaritiesRequest, EmbeddingsSimilaritiesResponse,
)


class EmbeddingsService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def get(self, req: EmbeddingsGetRequest) -> EmbeddingsGetResponse:
        r = await self._http.post("/embeddings/get/", json=req.model_dump())
        r.raise_for_status()
        return EmbeddingsGetResponse.model_validate(r.json())

    async def similarities(self, req: EmbeddingsSimilaritiesRequest) -> EmbeddingsSimilaritiesResponse:
        r = await self._http.post("/embeddings/similarities/", json=req.model_dump())
        r.raise_for_status()
        return EmbeddingsSimilaritiesResponse.model_validate(r.json())

    async def reduce(self, req: EmbeddingsReduceRequest) -> EmbeddingsReduceResponse:
        r = await self._http.post("/embeddings/reduce/", json=req.model_dump())
        r.raise_for_status()
        return EmbeddingsReduceResponse.model_validate(r.json())
