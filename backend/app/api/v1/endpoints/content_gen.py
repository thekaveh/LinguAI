from sqlalchemy.orm import Session
from sqlmodel import Session as SqlModelSession
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException

from app.utils.logger import log_decorator
from app.data_access.session import get_db
from app.schema.content_gen import ContentGenReq
from app.services.dependency.db_service import get_db_session
from app.services.content_gen_service import ContentGenService

router = APIRouter()


@log_decorator
@router.post("/content_gen/gen_by_content_topic")
async def generate_content_by_topic(
    request: ContentGenReq,
    db: Session = Depends(get_db),
    sql_model_session: SqlModelSession = Depends(get_db_session),
) -> StreamingResponse:
    """
    Generate content by topic.

    Args:
        request (ContentGenReq): The request object containing the topic information.
        db (Session): The database session.
        sql_model_session (SqlModelSession): The SQL model session.

    Returns:
        StreamingResponse: A streaming response containing the generated content.
    """
    service = ContentGenService(db, sql_model_session=sql_model_session)
    try:
        stream = await service.agenerate_content(request)
        return StreamingResponse(content=stream, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
