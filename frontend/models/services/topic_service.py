from __future__ import annotations
import httpx
from models.schemas.topic import Topic


class TopicService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list(self) -> list[Topic]:
        r = await self._http.get("/topics/list")
        r.raise_for_status()
        return [Topic.model_validate(x) for x in r.json()]
