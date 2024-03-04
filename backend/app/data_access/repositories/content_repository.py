from typing import Optional
from sqlalchemy.orm import Session

from app.utils.logger import log_decorator
from app.schema.content import ContentCreate
from app.data_access.models.content import Content
from app.data_access.repositories.base_repository import BaseRepository


class ContentRepository(BaseRepository[Content]):
    @log_decorator
    def __init__(self, db_session: Session):
        super().__init__(db_session, Content)

    @log_decorator
    def find_by_content_id(self, content_id: int) -> Optional[Content]:
        return (
            self.db_session.query(Content)
            .filter(Content.content_id == content_id)
            .first()
        )

    @log_decorator
    def find_by_content_name(self, content_name: str) -> Optional[Content]:
        return (
            self.db_session.query(Content)
            .filter(Content.content_name == content_name)
            .first()
        )

    @log_decorator
    def find_all(self):
        return self.db_session.query(Content).all()

    @log_decorator
    def update(self, content: Content, content_update: ContentCreate) -> Content:
        for key, value in content_update.dict().items():
            setattr(content, key, value)
        self.db_session.commit()
        self.db_session.refresh(content)
        return content

    @log_decorator
    def delete(self, content_id: int) -> None:
        content = self.find_by_content_id(content_id)
        if content:
            self.db_session.delete(content)
            self.db_session.commit()