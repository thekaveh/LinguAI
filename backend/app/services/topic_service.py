from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.data_models.topic import Topic
from app.repositories.topic_repository import TopicRepository
from app.models.schema.topic import TopicCreate, Topic as TopicSchema
from app.utils.logger import log_decorator

class TopicService:
    @log_decorator    
    def __init__(self, db: Session):
        self.db = db
        self.topic_repo = TopicRepository(db)
        
    @log_decorator
    def create_topic(self, topic_create: TopicCreate) -> TopicSchema:
        db_topic = self.topic_repo.create(Topic(topic_name=topic_create.topic_name))
        return TopicSchema(**db_topic.__dict__)
    
    @log_decorator
    def get_topic_by_id(self, topic_id: int) -> Optional[TopicSchema]:
        db_topic = self.topic_repo.find_by_topic_id(topic_id)
        if db_topic:
            return TopicSchema(**db_topic.__dict__)
        return None
    
    @log_decorator
    def get_all_topics(self) -> List[TopicSchema]:
        db_topics = self.topic_repo.find_all()
        return [TopicSchema(**topic.__dict__) for topic in db_topics]
    
    @log_decorator
    def update_topic(self, topic_id: int, topic_update: TopicCreate) -> Optional[TopicSchema]:
        db_topic = self.topic_repo.find_by_topic_id(topic_id)
        if db_topic:
            updated_topic = self.topic_repo.update(db_topic, topic_update)
            return TopicSchema(**updated_topic.__dict__)
        return None

    @log_decorator
    def delete_topic(self, topic_id: int) -> None:
        self.topic_repo.delete(topic_id)
