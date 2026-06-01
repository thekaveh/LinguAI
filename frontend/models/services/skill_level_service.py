from __future__ import annotations
import httpx
from models.schemas.skill_level import SkillLevelSchema


class SkillLevelService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list(self) -> list[SkillLevelSchema]:
        r = await self._http.get("/skill_levels/list")
        r.raise_for_status()
        return [SkillLevelSchema.model_validate(x) for x in r.json()]
