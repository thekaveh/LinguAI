from sqlmodel import Session
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException

from app.schema.chat import ChatRequest
from app.utils.logger import log_decorator
from app.services.chat_service import ChatService
from app.services.dependency.db_service import get_db_session

router = APIRouter()


@log_decorator
@router.post("/chat")
async def chat(
    request: ChatRequest, db_session: Session = Depends(get_db_session)
) -> StreamingResponse:
    try:
        service = ChatService(db_session)
        stream = await service.achat(request=request)
        return StreamingResponse(content=stream, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
