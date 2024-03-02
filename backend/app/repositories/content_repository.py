from .base_repository import BaseRepository
from sqlalchemy.orm import Session
from typing import Optional
from app.models.schema.content import ContentCreate

from app.models.data_models.content import Content

class ContentRepository(BaseRepository[Content]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, Content)

    def find_by_content_id(self, content_id: int) -> Optional[Content]:
        return self.db_session.query(Content).filter(Content.content_id == content_id).first()

    def find_by_content_name(self, content_name: str) -> Optional[Content]:
        return self.db_session.query(Content).filter(Content.content_name == content_name).first()

    def find_all(self):
        return self.db_session.query(Content).all()

    def update(self, content: Content, content_update: ContentCreate) -> Content:
        for key, value in content_update.dict().items():
            setattr(content, key, value)
        self.db_session.commit()
        self.db_session.refresh(content)
        return content

    def delete(self, content_id: int) -> None:
        content = self.find_by_content_id(content_id)
        if content:
            self.db_session.delete(content)
            self.db_session.commit()