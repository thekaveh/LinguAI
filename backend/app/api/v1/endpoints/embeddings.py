from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends

from app.utils.logger import log_decorator
from app.services.embeddings_service import EmbeddingsService
from app.services.dependency.db_service import get_db_session
from app.models.embeddings import (
    EmbeddingsGetRequest,
    EmbeddingsGetResponse,
    EmbeddingsReduceRequest,
    EmbeddingsReduceResponse,
    EmbeddingsSimilaritiesRequest,
    EmbeddingsSimilaritiesResponse,
)

router = APIRouter()


def _get_service(db_session: Session = Depends(get_db_session)) -> EmbeddingsService:
    return EmbeddingsService(db_session=db_session)


@log_decorator
@router.post("/embeddings/get/", response_model=EmbeddingsGetResponse)
def get(
    request: EmbeddingsGetRequest, service: EmbeddingsService = Depends(_get_service)
):
    try:
        return service.get(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.post("/embeddings/similarities/", response_model=EmbeddingsSimilaritiesResponse)
def similarities(
    request: EmbeddingsSimilaritiesRequest,
    service: EmbeddingsService = Depends(_get_service),
):
    try:
        return service.similarities(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.post("/embeddings/reduce/", response_model=EmbeddingsReduceResponse)
def reduce(
    request: EmbeddingsReduceRequest, service: EmbeddingsService = Depends(_get_service)
):
    try:
        return service.reduce(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
