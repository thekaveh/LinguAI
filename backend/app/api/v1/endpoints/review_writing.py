import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.utils.logger import log_decorator
from app.data_access.session import get_db
from app.schema.review_writing import ReviewWritingReq
from app.services.review_writing_service import ReviewWritingService

router = APIRouter()


@log_decorator
@router.post("/review_writing/")
async def review_writing(
    request: ReviewWritingReq, db: Session = Depends(get_db)
) -> StreamingResponse:
    
    review_writing_service = ReviewWritingService(db)
    try:
        stream = review_writing_service.review_writing(request)
        return StreamingResponse(content=stream, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))