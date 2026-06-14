from __future__ import annotations
import httpx

from models.schemas.language import Language


class LanguageService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list(self) -> list[Language]:
        r = await self._http.get("/languages/list")
        r.raise_for_status()
        return [Language.model_validate(x) for x in r.json()]

    async def get_by_name(self, name: str) -> Language:
        r = await self._http.get(f"/languages/{name}")
        r.raise_for_status()
        return Language.model_validate(r.json())
