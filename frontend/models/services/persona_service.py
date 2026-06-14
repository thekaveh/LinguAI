from __future__ import annotations
import httpx
from models.domain.persona import Persona


class PersonaService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list(self) -> list[Persona]:
        r = await self._http.get("/personas/")
        r.raise_for_status()
        return [Persona.model_validate(x) for x in r.json()]
