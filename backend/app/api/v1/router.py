from fastapi import APIRouter
from app.api.v1.endpoints import chat, llm, persona

router = APIRouter()

router.include_router(llm.router, prefix="/v1", tags=["v1"])
router.include_router(chat.router, prefix="/v1", tags=["v1"])
router.include_router(persona.router, prefix="/v1", tags=["v1"])