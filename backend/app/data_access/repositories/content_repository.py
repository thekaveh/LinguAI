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
        """
        Find a content by its content ID.

        Args:
            content_id (int): The ID of the content to find.

        Returns:
            Optional[Content]: The found content, or None if not found.
        """
        return (
            self.db_session.query(Content)
            .filter(Content.content_id == content_id)
            .first()
        )

    @log_decorator
    def find_by_content_name(self, content_name: str) -> Optional[Content]:
        """
        Find a content by its name.

        Args:
            content_name (str): The name of the content to search for.

        Returns:
            Optional[Content]: The found content, or None if not found.
        """
        return (
            self.db_session.query(Content)
            .filter(Content.content_name == content_name)
            .first()
        )

    @log_decorator
    def find_all(self):
        """
        Retrieves all content from the database.

        Returns:
            A list of Content objects representing all the content in the database.
        """
        return self.db_session.query(Content).all()

    @log_decorator
    def update(self, content: Content, content_update: ContentCreate) -> Content:
        """
        Update the content object with the provided content_update data.

        Args:
            content (Content): The content object to be updated.
            content_update (ContentCreate): The updated content data.

        Returns:
            Content: The updated content object.
        """
        for key, value in content_update.dict().items():
            setattr(content, key, value)
        self.db_session.commit()
        self.db_session.refresh(content)
        return content

    @log_decorator
    def delete(self, content_id: int) -> None:
        """
        Deletes content from the database.

        Args:
            content_id (int): The ID of the content to be deleted.

        Returns:
            None
        """
        content = self.find_by_content_id(content_id)
        if content:
            self.db_session.delete(content)
            self.db_session.commit()
