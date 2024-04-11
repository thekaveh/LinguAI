from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends

from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.services.dependency.db_service import get_db_session

router = APIRouter()


def _get_service(db_session: Session = Depends(get_db_session)) -> LLMService:
    return LLMService(db_session=db_session)


@log_decorator
@router.get("/llms/all/")
def get_all(service: LLMService = Depends(_get_service)):
    try:
        return service.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/llms/embeddings/")
def get_embeddings(service: LLMService = Depends(_get_service)):
    try:
        return service.get_embeddings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/llms/content/")
def get_content(service: LLMService = Depends(_get_service)):
    try:
        return service.get_content()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/llms/vision/")
def get_vision(service: LLMService = Depends(_get_service)):
    try:
        return service.get_vision()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/llms/chat/")
def get_chat(service: LLMService = Depends(_get_service)):
    try:
        return service.get_chat()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/llms/by_name/{name}", response_model=None)
def get_by_name(name: str, service: LLMService = Depends(_get_service)):
    llm = service.get_by_name(name)

    if llm is None:
        raise HTTPException(status_code=404, detail="LLM not found!")

    return llm


@log_decorator
@router.get("/llms/by_id/{id}", response_model=None)
def get_by_id(id: int, service: LLMService = Depends(_get_service)):
    llm = service.get_by_id(id)

    if llm is None:
        raise HTTPException(status_code=404, detail="LLM not found!")

    return llm
