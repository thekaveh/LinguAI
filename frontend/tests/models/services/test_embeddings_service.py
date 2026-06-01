from __future__ import annotations
import httpx
import pytest
import respx

from models.services.embeddings_service import EmbeddingsService
from models.domain.embeddings import (
    EmbeddingsGetRequest, EmbeddingsSimilaritiesRequest, EmbeddingsReduceRequest,
)


@pytest.mark.asyncio
async def test_get_embeddings():
    async with httpx.AsyncClient(base_url="http://test/v1") as http:
        with respx.mock() as router:
            router.post("http://test/v1/embeddings/get/").mock(
                return_value=httpx.Response(200, json={"embeddings": [[0.1, 0.2], [0.3, 0.4]]})
            )
            svc = EmbeddingsService(http)
            r = await svc.get(EmbeddingsGetRequest(llm_id=1, texts=["a", "b"]))
            assert r.embeddings == [[0.1, 0.2], [0.3, 0.4]]


@pytest.mark.asyncio
async def test_similarities():
    async with httpx.AsyncClient(base_url="http://test/v1") as http:
        with respx.mock() as router:
            router.post("http://test/v1/embeddings/similarities/").mock(
                return_value=httpx.Response(200, json={"similarities": [0.9, 0.8]})
            )
            svc = EmbeddingsService(http)
            r = await svc.similarities(EmbeddingsSimilaritiesRequest(embeddings=[[0.1], [0.2]]))
            assert r.similarities == [0.9, 0.8]


@pytest.mark.asyncio
async def test_reduce_uses_target_dims_field():
    async with httpx.AsyncClient(base_url="http://test/v1") as http:
        with respx.mock() as router:
            router.post("http://test/v1/embeddings/reduce/").mock(
                return_value=httpx.Response(200, json={"reduced_embeddings": [[0.1, 0.2], [0.3, 0.4]]})
            )
            svc = EmbeddingsService(http)
            r = await svc.reduce(EmbeddingsReduceRequest(embeddings=[[0.1, 0.2, 0.3]], target_dims=2))
            assert r.reduced_embeddings[0] == [0.1, 0.2]
