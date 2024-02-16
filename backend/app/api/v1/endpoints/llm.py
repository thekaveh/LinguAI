from langserve import add_routes
from fastapi import APIRouter, HTTPException
from typing import AsyncIterable, List, Tuple
from fastapi.responses import StreamingResponse

from app.services.llm_service import LLMService
from app.models.shared.request_models.ChatRequest import ChatRequest

router = APIRouter()

@router.get("/llm/list")
async def list():
    try:
        result = LLMService.list_models()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
	try:
		stream = await LLMService.achat(
      		model=request.model
      		, messages=request.messages
         	, temperature=request.temperature
        )
		return StreamingResponse(stream, media_type="text/event-stream")
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))