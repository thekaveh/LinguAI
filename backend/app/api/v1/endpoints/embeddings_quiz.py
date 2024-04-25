from sqlmodel import Session
from fastapi import APIRouter, Depends, HTTPException

from app.utils.logger import log_decorator
from app.services.dependency.db_service import get_db_session
from app.services.embeddings_quiz_service import EmbeddingsQuizService
from app.models.embeddings_quiz import (
    EmbeddingsQuizRequest,
    EmbeddingsQuizResponse,
)

router = APIRouter()


@log_decorator
@router.post("/embeddings_quiz/generate")
async def generate(
    request: EmbeddingsQuizRequest, db_session: Session = Depends(get_db_session)
) -> EmbeddingsQuizResponse:
    try:
        service = EmbeddingsQuizService(db_session)
        return await service.agenerate(request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
