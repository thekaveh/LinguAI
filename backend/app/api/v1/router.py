from fastapi import APIRouter
from app.api.v1.endpoints import joke

router = APIRouter()

router.include_router(joke.router, prefix="/v1", tags=["v1"])
