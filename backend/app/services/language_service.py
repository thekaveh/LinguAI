from typing import List, Optional
from sqlmodel import Session, select

from app.models.language import Language
from app.utils.logger import log_decorator
from app.services.crud_service import CRUDService


class LanguageService(CRUDService[Language]):
    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @log_decorator
    def get_all(self) -> List[Language]:
        languages = self.db_session.exec(select(Language)).all()

        return languages

    @log_decorator
    def get_by_id(self, id: int) -> Optional[Language]:
        language = self.db_session.get(Language, id)

        return language

    @log_decorator
    def get_by_name(self, name: str) -> Optional[Language]:
        query = select(Language).where(Language.language_name == name)

        return self.db_session.exec(query).first()

    @log_decorator
    def create(self, entity: Language) -> Language:
        self.db_session.add(entity)
        self.db_session.commit()
        self.db_session.refresh(entity)

        return entity

    @log_decorator
    def update(self, id: int, value: Language) -> Optional[Language]:
        language = self.db_session.get(Language, id)

        if not language:
            return None

        data = value.dict(exclude_unset=True)

        for key, value in data.items():
            setattr(language, key, value)

        self.db_session.add(language)
        self.db_session.commit()
        self.db_session.refresh(language)

        return language

    @log_decorator
    def delete(self, id: int) -> None:
        language = self.db_session.get(Language, id)

        if language:
            self.db_session.delete(language)
            self.db_session.commit()
