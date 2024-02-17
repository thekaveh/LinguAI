from typing import List
from fastapi import APIRouter, HTTPException

from app.models.list_res import ListRes
from app.services.persona_service import PersonaService

router = APIRouter()

@router.get("/persona/list")
async def list() -> ListRes:
    try:
        return ListRes(result=PersonaService.list_personas())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))