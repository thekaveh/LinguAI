from sqlalchemy.orm import Session
from typing import Optional, List

from app.utils.logger import log_decorator
from app.data_access.models.content import Content
from app.schema.content import ContentCreate, Content as ContentSchema
from app.data_access.repositories.content_repository import ContentRepository


class ContentService:
    """
    Service class for managing content.
    """

    @log_decorator
    def __init__(self, db: Session):
        self.db = db
        self.content_repo = ContentRepository(db)

    @log_decorator
    def create_content(self, content_create: ContentCreate) -> ContentSchema:
        """
        Create a new content.

        Args:
            content_create (ContentCreate): The content data to create.

        Returns:
            ContentSchema: The created content.
        """
        db_content = self.content_repo.create(
            Content(content_name=content_create.content_name)
        )
        return ContentSchema(**db_content.__dict__)

    @log_decorator
    def get_content_by_id(self, content_id: int) -> Optional[ContentSchema]:
        """
        Get content by ID.

        Args:
            content_id (int): The ID of the content.

        Returns:
            Optional[ContentSchema]: The content if found, None otherwise.
        """
        db_content = self.content_repo.find_by_content_id(content_id)
        if db_content:
            return ContentSchema(**db_content.__dict__)
        return None

    @log_decorator
    def get_all_content(self) -> List[ContentSchema]:
        """
        Get all content.

        Returns:
            List[ContentSchema]: A list of all content.
        """
        db_content = self.content_repo.find_all()
        return [ContentSchema(**content.__dict__) for content in db_content]

    @log_decorator
    def update_content(
        self, content_id: int, content_update: ContentCreate
    ) -> Optional[ContentSchema]:
        """
        Update content.

        Args:
            content_id (int): The ID of the content to update.
            content_update (ContentCreate): The updated content data.

        Returns:
            Optional[ContentSchema]: The updated content if found, None otherwise.
        """
        db_content = self.content_repo.find_by_content_id(content_id)
        if db_content:
            updated_content = self.content_repo.update(db_content, content_update)
            return ContentSchema(**updated_content.__dict__)
        return None

    @log_decorator
    def delete_content(self, content_id: int) -> None:
        """
        Delete content.

        Args:
            content_id (int): The ID of the content to delete.
        """
        self.content_repo.delete(content_id)
