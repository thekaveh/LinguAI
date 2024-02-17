from typing import List
from fastapi import APIRouter, HTTPException

from app.models.list_res import ListRes
from app.services.llm_service import LLMService

router = APIRouter()

@router.get("/llm/list")
async def list() -> ListRes:
    try:
        return ListRes(result=LLMService.list_models())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))