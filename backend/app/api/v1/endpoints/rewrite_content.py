from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.utils.logger import log_decorator
from app.data_access.session import get_db
from app.schema.rewrite_content import ContentRewriteReq
from app.services.rewrite_content_service import RewriteContentService

router = APIRouter()


@log_decorator
@router.post("/rewrite_content/")
async def rewrite_content(
    request: ContentRewriteReq, db: Session = Depends(get_db)
) -> StreamingResponse:
    rewrite_service = RewriteContentService(db)
    try:
        stream = rewrite_service.rewrite_content(request)
        return StreamingResponse(content=stream, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
