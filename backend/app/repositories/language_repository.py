from .base_repository import BaseRepository
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.data_models.language import Language

class LanguageRepository(BaseRepository[Language]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, Language)

    def find_by_id(self, language_id: int) -> Optional[Language]:
        return self.db_session.query(Language).filter(Language.language_id == language_id).first()

    def find_by_name(self, language_name: str) -> Optional[Language]:
        return self.db_session.query(Language).filter(Language.language_name == language_name).first()

    def get_all_languages(self) -> List[Language]:
        return self.db_session.query(Language).all()