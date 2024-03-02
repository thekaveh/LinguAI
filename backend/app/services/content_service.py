from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.data_models.content import Content
from app.repositories.content_repository import ContentRepository
from app.models.schema.content import ContentCreate, Content as ContentSchema

class ContentService:
    def __init__(self, db: Session):
        self.db = db
        self.content_repo = ContentRepository(db)

    def create_content(self, content_create: ContentCreate) -> ContentSchema:
        db_content = self.content_repo.create(Content(content_name=content_create.content_name))
        return ContentSchema(**db_content.__dict__)

    def get_content_by_id(self, content_id: int) -> Optional[ContentSchema]:
        db_content = self.content_repo.find_by_content_id(content_id)
        if db_content:
            return ContentSchema(**db_content.__dict__)
        return None

    def get_all_content(self) -> List[ContentSchema]:
        db_content = self.content_repo.find_all()
        return [ContentSchema(**content.__dict__) for content in db_content]

    def update_content(self, content_id: int, content_update: ContentCreate) -> Optional[ContentSchema]:
        db_content = self.content_repo.find_by_content_id(content_id)
        if db_content:
            updated_content = self.content_repo.update(db_content, content_update)
            return ContentSchema(**updated_content.__dict__)
        return None

    def delete_content(self, content_id: int) -> None:
        self.content_repo.delete(content_id)