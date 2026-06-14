from sqlalchemy.orm import Session
from typing import List, Optional

from app.schema.topic import TopicCreate
from app.utils.logger import log_decorator
from app.data_access.models.topic import Topic
from app.data_access.repositories.base_repository import BaseRepository


class TopicRepository(BaseRepository[Topic]):
    """
    Repository class for managing Topic objects in the database.

    Args:
        db_session (Session): The database session object.

    Attributes:
        db_session (Session): The database session object.

    """

    @log_decorator
    def __init__(self, db_session: Session):
        super().__init__(db_session, Topic)

    @log_decorator
    def find_by_topic_id(self, topic_id: int) -> Optional[Topic]:
        """
        Find a topic by its ID.

        Args:
            topic_id (int): The ID of the topic to find.

        Returns:
            Optional[Topic]: The found topic, or None if not found.

        """
        return self.db_session.query(Topic).filter(Topic.topic_id == topic_id).first()

    @log_decorator
    def find_by_topic_name(self, topic_name: str) -> Optional[Topic]:
        """
        Find a topic by its name.

        Args:
            topic_name (str): The name of the topic to find.

        Returns:
            Optional[Topic]: The found topic, or None if not found.

        """
        return (
            self.db_session.query(Topic).filter(Topic.topic_name == topic_name).first()
        )

    @log_decorator
    def find_all(self) -> List[Topic]:
        """
        Find all topics.

        Returns:
            List[Topic]: A list of all topics.

        """
        return self.db_session.query(Topic).all()

    @log_decorator
    def update(self, topic: Topic, topic_update: TopicCreate) -> Topic:
        """
        Update a topic.

        Args:
            topic (Topic): The topic to update.
            topic_update (TopicCreate): The updated topic data.

        Returns:
            Topic: The updated topic.

        """
        for key, value in topic_update.dict().items():
            setattr(topic, key, value)
        self.db_session.commit()
        self.db_session.refresh(topic)
        return topic

    @log_decorator
    def delete(self, topic_id: int) -> None:
        """
        Delete a topic.

        Args:
            topic_id (int): The ID of the topic to delete.

        """
        topic = self.find_by_topic_id(topic_id)
        if topic:
            self.db_session.delete(topic)
            self.db_session.commit()
