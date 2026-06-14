from __future__ import annotations
import httpx

from models.schemas.text_to_speech import TextToSpeechRequest, TextToSpeechResponse


class TextToSpeechService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def synthesize(self, req: TextToSpeechRequest) -> TextToSpeechResponse:
        r = await self._http.post("/text_to_speech", json=req.model_dump(mode="json"),
                                   timeout=httpx.Timeout(connect=5.0, read=60.0, write=15.0, pool=15.0))
        r.raise_for_status()
        return TextToSpeechResponse.model_validate(r.json())
