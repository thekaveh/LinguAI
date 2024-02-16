from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.chat_service import ChatService
from app.models.shared.request_models.ChatRequest import ChatRequest

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
	try:
		stream = await ChatService.achat(
			model=request.model
			, messages=request.messages
			, temperature=request.temperature
        )
		return StreamingResponse(stream, media_type="text/event-stream")
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))