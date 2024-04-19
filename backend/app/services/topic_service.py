from sqlalchemy.orm import Session
from typing import Optional, List

from app.utils.logger import log_decorator
from app.data_access.models.topic import Topic
from app.schema.topic import TopicCreate, Topic as TopicSchema
from app.data_access.repositories.topic_repository import TopicRepository


class TopicService:
    """
    This class provides methods to interact with topics in the database.
    """

    @log_decorator
    def __init__(self, db: Session):
        """
        Initializes a new instance of the TopicService class.

        Args:
            db (Session): The database session object.
        """
        self.db = db
        self.topic_repo = TopicRepository(db)

    @log_decorator
    def create_topic(self, topic_create: TopicCreate) -> TopicSchema:
        """
        Creates a new topic.

        Args:
            topic_create (TopicCreate): The topic creation data.

        Returns:
            TopicSchema: The created topic.
        """
        db_topic = self.topic_repo.create(Topic(topic_name=topic_create.topic_name))
        return TopicSchema(**db_topic.__dict__)

    @log_decorator
    def get_topic_by_id(self, topic_id: int) -> Optional[TopicSchema]:
        """
        Retrieves a topic by its ID.

        Args:
            topic_id (int): The ID of the topic.

        Returns:
            Optional[TopicSchema]: The retrieved topic, or None if not found.
        """
        db_topic = self.topic_repo.find_by_topic_id(topic_id)
        if db_topic:
            return TopicSchema(**db_topic.__dict__)
        return None

    @log_decorator
    def get_all_topics(self) -> List[TopicSchema]:
        """
        Retrieves all topics.

        Returns:
            List[TopicSchema]: The list of all topics.
        """
        db_topics = self.topic_repo.find_all()
        return [TopicSchema(**topic.__dict__) for topic in db_topics]

    @log_decorator
    def update_topic(
        self, topic_id: int, topic_update: TopicCreate
    ) -> Optional[TopicSchema]:
        """
        Updates a topic.

        Args:
            topic_id (int): The ID of the topic to update.
            topic_update (TopicCreate): The updated topic data.

        Returns:
            Optional[TopicSchema]: The updated topic, or None if not found.
        """
        db_topic = self.topic_repo.find_by_topic_id(topic_id)
        if db_topic:
            updated_topic = self.topic_repo.update(db_topic, topic_update)
            return TopicSchema(**updated_topic.__dict__)
        return None

    @log_decorator
    def delete_topic(self, topic_id: int) -> None:
        """
        Deletes a topic.

        Args:
            topic_id (int): The ID of the topic to delete.
        """
        self.topic_repo.delete(topic_id)
