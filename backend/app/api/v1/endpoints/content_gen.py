# Backend: FastAPI Streaming Endpoint Adjustment

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

from app.services.content_gen_service import ContentGenService
from app.models.schema.content_gen import ContentGenReq

router = APIRouter()

@router.post("/content_gen/gen_by_content_topic")
async def generate_content_by_topic(request: ContentGenReq) -> StreamingResponse:
    try:
        stream = ContentGenService.generate_content(request)
        return StreamingResponse(content=stream, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))