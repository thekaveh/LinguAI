from __future__ import annotations
import httpx
from models.schemas.content import Content


class ContentService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list(self) -> list[Content]:
        r = await self._http.get("/contents/list")
        r.raise_for_status()
        return [Content.model_validate(x) for x in r.json()]
