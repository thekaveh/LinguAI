# Backend: FastAPI Streaming Endpoint Adjustment

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from sqlalchemy.orm import Session
from app.repositories.data_access.session import get_db
from app.services.content_gen_service import ContentGenService
from app.models.schema.content_gen import ContentGenReq
from app.utils.logger import log_decorator

router = APIRouter()

@log_decorator
@router.post("/content_gen/gen_by_content_topic")
async def generate_content_by_topic(request: ContentGenReq, db: Session = Depends(get_db)) -> StreamingResponse:
    con_gen_service = ContentGenService(db)
    try:
        stream = con_gen_service.generate_content(request)
        return StreamingResponse(content=stream, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))