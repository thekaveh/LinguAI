from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.chat_service import ChatService
from app.models.common.chat_request import ChatRequest

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    try:
        stream = await ChatService.achat(request=request)
        return StreamingResponse(content=stream, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
