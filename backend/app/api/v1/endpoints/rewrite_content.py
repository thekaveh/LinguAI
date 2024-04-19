from sqlalchemy.orm import Session
from sqlmodel import Session as SqlModelSession
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException

from app.utils.logger import log_decorator
from app.data_access.session import get_db
from app.schema.rewrite_content import ContentRewriteReq
from app.services.dependency.db_service import get_db_session
from app.services.rewrite_content_service import RewriteContentService

router = APIRouter()


@log_decorator
@router.post("/rewrite_content/")
async def rewrite_content(
    request: ContentRewriteReq,
    db: Session = Depends(get_db),
    sql_model_session: SqlModelSession = Depends(get_db_session),
) -> StreamingResponse:
    """
    Rewrite the content based on the given request.

    Args:
        request (ContentRewriteReq): The request object containing the content to be rewritten.
        db (Session): The database session.
        sql_model_session (SqlModelSession): The SQL model session.

    Returns:
        StreamingResponse: The streaming response containing the rewritten content.
    """
    rewrite_service = RewriteContentService(db, sql_model_session=sql_model_session)
    try:
        stream = await rewrite_service.arewrite_content(request)
        return StreamingResponse(content=stream, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
