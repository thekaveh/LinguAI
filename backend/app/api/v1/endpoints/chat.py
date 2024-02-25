from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.chat_service import ChatService
from app.models.messages.chat_message import ChatMessage

router = APIRouter()


@router.post("/chat")
async def chat(message: ChatMessage) -> StreamingResponse:
    try:
        stream = await ChatService.achat(message=message)
        return StreamingResponse(content=stream, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
