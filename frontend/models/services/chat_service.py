from __future__ import annotations
from typing import AsyncIterator
import httpx

from models.schemas.chat import ChatRequest


class ChatService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def stream(self, req: ChatRequest) -> AsyncIterator[str]:
        """Yield response chunks as they stream from the backend (text/event-stream).

        Backend returns raw text per SSE-style chunk; we surface them as-is.
        Caller is responsible for appending each chunk to the in-flight assistant bubble.
        """
        async with self._http.stream(
            "POST", "/chat",
            json=req.model_dump(mode="json"),
            timeout=httpx.Timeout(connect=5.0, read=60.0, write=15.0, pool=15.0),
        ) as r:
            r.raise_for_status()
            async for chunk in r.aiter_text():
                if chunk:
                    yield chunk
