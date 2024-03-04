from app.schema.topic import TopicCreate
from app.utils.logger import log_decorator
from .base_repository import BaseRepository
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.data_models.topic import Topic


class TopicRepository(BaseRepository[Topic]):
    @log_decorator
    def __init__(self, db_session: Session):
        super().__init__(db_session, Topic)

    @log_decorator
    def find_by_topic_id(self, topic_id: int) -> Optional[Topic]:
        return self.db_session.query(Topic).filter(Topic.topic_id == topic_id).first()

    @log_decorator
    def find_by_topic_name(self, topic_name: str) -> Optional[Topic]:
        return (
            self.db_session.query(Topic).filter(Topic.topic_name == topic_name).first()
        )

    @log_decorator
    def find_all(self) -> List[Topic]:
        return self.db_session.query(Topic).all()

    @log_decorator
    def update(self, topic: Topic, topic_update: TopicCreate) -> Topic:
        for key, value in topic_update.dict().items():
            setattr(topic, key, value)
        self.db_session.commit()
        self.db_session.refresh(topic)
        return topic

    @log_decorator
    def delete(self, topic_id: int) -> None:
        topic = self.find_by_topic_id(topic_id)
        if topic:
            self.db_session.delete(topic)
            self.db_session.commit()
