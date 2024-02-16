import httpx

from httpx import Timeout
from pydantic import BaseModel
from typing import AsyncIterable

class HttpUtils:
    @staticmethod
    async def apost_stream(url: str, request: BaseModel) -> AsyncIterable[str]:
        timeout = Timeout(60.0, connect=15.0, read=45.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, json=request.dict()) as response:
                async for chunk in response.aiter_text():
                    yield chunk