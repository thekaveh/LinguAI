from typing import List
from fastapi import APIRouter, HTTPException

from app.services.llm_service import LLMService
from app.models.messages.list_message import ListMessage

router = APIRouter()


@router.get("/llm/list")
async def list() -> ListMessage:
    try:
        return ListMessage(result=LLMService.list_models())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
