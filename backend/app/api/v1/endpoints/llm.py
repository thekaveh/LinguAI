from fastapi import APIRouter, HTTPException

from app.services.llm_service import LLMService
from app.models.common.list_response import ListResponse

router = APIRouter()


@router.get("/llm/list_models")
async def list() -> ListResponse:
    try:
        return ListResponse(result=LLMService.list_models())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/llm/list_vision_models")
async def list_vision_models() -> ListResponse:
    try:
        return ListResponse(result=LLMService.list_vision_models())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
