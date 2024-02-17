import httpx

from httpx import HTTPStatusError, RequestError, Timeout
from pydantic import BaseModel, parse_obj_as, ValidationError
from typing import Any, AsyncIterable, Dict, Optional, Generic, Type, TypeVar

T = TypeVar('T')

class HttpUtils:
    @staticmethod
    async def apost_stream(url: str, request: BaseModel, timeout: Optional[Timeout] = None) -> AsyncIterable[str]:
        if timeout is None:
            timeout = Timeout(60.0, connect=15.0, read=45.0)
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("POST", url, json=request.dict()) as response:
                    response.raise_for_status()

                    async for chunk in response.aiter_text():
                        yield chunk
        except (HTTPStatusError, RequestError) as e:
            raise Exception(f"HTTP error occurred: {e}") from e
        
    @staticmethod
    async def get(
        url: str
        , response_model: Type[T]
        , params: Optional[Dict[str, Any]] = None
        , timeout: Optional[Timeout] = None
    ) -> T:
        if timeout is None:
            timeout = Timeout(60.0, connect=15.0, read=45.0)
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                try:
                    return parse_obj_as(response_model, response.json())
                except ValidationError as e:
                    raise ValueError(f"Error casting response to model {response_model}: {e}") from e
        except (HTTPStatusError, RequestError) as e:
            raise Exception(f"HTTP error occurred: {e}") from e
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}") from e