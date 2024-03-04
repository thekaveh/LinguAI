from typing import List
from fastapi import APIRouter, HTTPException

from app.services.persona_service import PersonaService
from app.models.common.list_response import ListResponse
from app.utils.logger import log_decorator

router = APIRouter()


@log_decorator
@router.get("/persona/list")
async def list() -> ListResponse:
    try:
        return ListResponse(result=PersonaService.list_personas())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
