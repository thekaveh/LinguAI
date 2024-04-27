from sqlmodel import Session
from fastapi import APIRouter, Depends, HTTPException

from app.utils.logger import log_decorator
from app.services.dependency.db_service import get_db_session
from app.services.polyglot_puzzle_service import PolyglotPuzzleService
from app.models.polyglot_puzzle import (
    PolyglotPuzzleRequest,
    PolyglotPuzzleResponse,
)

router = APIRouter()


@log_decorator
@router.post("/polyglot_puzzle/generate")
async def generate(
    request: PolyglotPuzzleRequest, db_session: Session = Depends(get_db_session)
) -> PolyglotPuzzleResponse:
    try:
        service = PolyglotPuzzleService(db_session)
        return await service.agenerate(request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
