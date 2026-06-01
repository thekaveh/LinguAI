from __future__ import annotations
import httpx

from models.domain.llm import LLM


class LLMService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list_all(self) -> list[LLM]:
        r = await self._http.get("/llms/all/")
        r.raise_for_status()
        return [LLM.model_validate(x) for x in r.json()]

    async def get_structured_content(self) -> list[LLM]:
        r = await self._http.get("/llms/structured_content/")
        r.raise_for_status()
        return [LLM.model_validate(x) for x in r.json()]

    async def get_embeddings(self) -> list[LLM]:
        r = await self._http.get("/llms/embeddings/")
        r.raise_for_status()
        return [LLM.model_validate(x) for x in r.json()]

    async def get_content(self) -> list[LLM]:
        r = await self._http.get("/llms/content/")
        r.raise_for_status()
        return [LLM.model_validate(x) for x in r.json()]

    async def get_vision(self) -> list[LLM]:
        r = await self._http.get("/llms/vision/")
        r.raise_for_status()
        return [LLM.model_validate(x) for x in r.json()]
