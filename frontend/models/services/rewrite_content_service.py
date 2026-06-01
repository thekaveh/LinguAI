from __future__ import annotations
from typing import AsyncIterator
import httpx

from models.schemas.rewrite_content import ContentRewriteReq


class RewriteContentService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def stream(self, req: ContentRewriteReq) -> AsyncIterator[str]:
        async with self._http.stream(
            "POST", "/rewrite_content/",
            json=req.model_dump(mode="json"),
            timeout=httpx.Timeout(connect=5.0, read=60.0, write=15.0, pool=15.0),
        ) as r:
            r.raise_for_status()
            async for chunk in r.aiter_text():
                if chunk:
                    yield chunk
