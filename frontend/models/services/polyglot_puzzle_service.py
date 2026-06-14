from __future__ import annotations
import httpx

from models.domain.polyglot_puzzle import PolyglotPuzzleRequest, PolyglotPuzzleResponse


class PolyglotPuzzleService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def generate(self, request: PolyglotPuzzleRequest) -> PolyglotPuzzleResponse:
        r = await self._http.post("/polyglot_puzzle/generate", json=request.model_dump())
        r.raise_for_status()
        return PolyglotPuzzleResponse.model_validate(r.json())
