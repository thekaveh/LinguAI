from fastapi import APIRouter
from app.api.v1.endpoints import joke, llm

router = APIRouter()

router.include_router(joke.router, prefix="/v1", tags=["v1"])
router.include_router(llm.router, prefix="/v1", tags=["v1"])