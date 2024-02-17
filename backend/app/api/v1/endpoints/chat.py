from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.chat_req import ChatReq
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatReq) -> StreamingResponse:
	try:
		stream = await ChatService.achat(
			model=request.model
			, messages=request.messages
			, temperature=request.temperature
        )
		return StreamingResponse(stream, media_type="text/event-stream")
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))