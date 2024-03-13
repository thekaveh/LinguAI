from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends

from app.models.language import Language
from app.utils.logger import log_decorator
from app.services.language_service import LanguageService
from app.services.dependency.db_service import get_db_session

router = APIRouter()


def _get_service(db_session: Session = Depends(get_db_session)) -> LanguageService:
    return LanguageService(db_session=db_session)


@log_decorator
@router.get("/languages/")
def get_all(service: LanguageService = Depends(_get_service)):
    try:
        return service.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/languages/by_id/{id}", response_model=None)
def get_by_id(id: int, service: LanguageService = Depends(_get_service)):
    language = service.get_by_id(id)

    if language is None:
        raise HTTPException(status_code=404, detail="Language not found!")

    return language


@log_decorator
@router.get("/languages/by_name/{name}", response_model=None)
def get_by_name(name: str, service: LanguageService = Depends(_get_service)):
    language = service.get_by_name(name)

    if language is None:
        raise HTTPException(status_code=404, detail="Language not found!")

    return language


@router.post("/languages/")
def create(language: Language, service: LanguageService = Depends(_get_service)):
    try:
        return service.create(language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.put("/languages/{id}")
def update(
    id: int, language: Language, service: LanguageService = Depends(_get_service)
):
    updated = service.update(id, language)

    if updated is None:
        raise HTTPException(status_code=404, detail="Language not found!")

    return updated


@log_decorator
@router.delete("/languages/{id}", response_model=None)
def delete(id: int, service: LanguageService = Depends(_get_service)):
    try:
        service.delete(id)
        return {"message": "Language deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
