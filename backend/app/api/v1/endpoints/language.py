from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.utils.logger import log_decorator
from app.data_access.session import get_db
from app.services.language_service import LanguageService
from app.schema.language import Language as LanguageSchema

router = APIRouter()


@log_decorator
@router.get("/languages/list", response_model=list[LanguageSchema])
def read_languages(db: Session = Depends(get_db)):
    language_service = LanguageService(db)
    return language_service.get_all_languages()


@log_decorator
@router.get("/languages/{language_name}", response_model=LanguageSchema)
def read_language_by_name(language_name: str, db: Session = Depends(get_db)):
    language_service = LanguageService(db)
    language = language_service.get_language_by_name(language_name)
    if language is None:
        raise HTTPException(status_code=404, detail="Language not found")
    return language
