from typing import Optional, List
from sqlalchemy.orm import Session

from app.utils.logger import log_decorator
from app.data_access.models.language import Language
from app.data_access.repositories.base_repository import BaseRepository


class LanguageRepository(BaseRepository[Language]):
    @log_decorator
    def __init__(self, db_session: Session):
        super().__init__(db_session, Language)

    @log_decorator
    def find_by_id(self, language_id: int) -> Optional[Language]:
        return (
            self.db_session.query(Language)
            .filter(Language.language_id == language_id)
            .first()
        )

    @log_decorator
    def find_by_name(self, language_name: str) -> Optional[Language]:
        return (
            self.db_session.query(Language)
            .filter(Language.language_name == language_name)
            .first()
        )

    @log_decorator
    def get_all_languages(self) -> List[Language]:
        return self.db_session.query(Language).all()
