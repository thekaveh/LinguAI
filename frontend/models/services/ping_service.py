from __future__ import annotations
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class PingResult:
    ok: bool
    message: str


class PingService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def ping(self) -> PingResult:
        try:
            r = await self._http.get("/health")
            r.raise_for_status()
            payload = r.json()
            return PingResult(ok=True, message=str(payload.get("message", payload)))
        except Exception as e:
            # Broad on purpose: this is a health probe whose failure must always
            # surface as ok=False, never propagate (e.g. a non-JSON 200 body would
            # raise JSONDecodeError, which httpx.HTTPError would miss) and crash the
            # admin ping background task.
            return PingResult(ok=False, message=f"ping failed: {e}")
