from typing import List
from fastapi import APIRouter, HTTPException

from app.services.persona_service import PersonaService
from app.models.messages.list_message import ListMessage

router = APIRouter()


@router.get("/persona/list")
async def list() -> ListMessage:
    try:
        return ListMessage(result=PersonaService.list_personas())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
