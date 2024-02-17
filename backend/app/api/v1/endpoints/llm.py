from typing import List
from fastapi import APIRouter, HTTPException

from app.services.llm_service import LLMService
from app.models.llm_list_res import LLMListRes

router = APIRouter()

@router.get("/llm/list")
async def list() -> LLMListRes:
    try:
        return LLMListRes(result=LLMService.list_models())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))