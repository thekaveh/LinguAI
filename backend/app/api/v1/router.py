from fastapi import APIRouter
from app.api.v1.endpoints import llm

router = APIRouter()

router.include_router(llm.router, prefix="/v1", tags=["v1"])