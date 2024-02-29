from typing import List
from fastapi import APIRouter, HTTPException

from app.services.persona_service import PersonaService
from app.models.common.list_response import ListResponse

router = APIRouter()


@router.get("/persona/list")
async def list() -> ListResponse:
    try:
        return ListResponse(result=PersonaService.list_personas())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
