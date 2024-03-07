from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException

from app.schema.chat import ChatRequest
from app.data_access.session import get_db
from app.utils.logger import log_decorator
from app.services.chat_service import ChatService

router = APIRouter()


@log_decorator
@router.post("/chat")
async def chat(
    request: ChatRequest, db_session: Session = Depends(get_db)
) -> StreamingResponse:
    try:
        service = ChatService(db_session)
        stream = await service.achat(request=request)
        return StreamingResponse(content=stream, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
