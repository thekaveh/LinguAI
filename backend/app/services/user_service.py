from sqlalchemy.orm import Session
from app.models.data_models.user import User as DBUser, UserTopic
from app.models.schema.user import User, UserCreate
from app.models.schema.topic import Topic
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def create_user(self, user_create: UserCreate) -> User:
        db_user = DBUser(
            username=user_create.username,
            email=user_create.email,
            password_hash=user_create.password_hash,
            user_type=user_create.user_type,
            base_language=user_create.base_language,
            learning_languages=user_create.learning_languages,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            middle_name=user_create.middle_name,
            mobile_phone=user_create.mobile_phone,
            landline_phone=user_create.landline_phone,
            contact_preference=user_create.contact_preference
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_id(self, user_id: int) -> User:
        db_user = self.user_repo.find_by_id(user_id)
        return db_user

    def get_users(self) -> list:
        return self.user_repo.get_all_users()
    
    def add_topic_to_user(self, user_id: int, topic_name: str) -> None:
        db_user = self.user_repo.find_by_id(user_id)
        if db_user:
            topic = self.db.query(UserTopic).filter(UserTopic.user_id == user_id, UserTopic.topic_name == topic_name).first()
            if topic:
                db_user.user_topics.append(topic)
                self.db.commit()

    def update_user_topics(self, user_id: int, new_topics: list) -> None:
        self.db.query(UserTopic).filter(UserTopic.user_id == user_id).delete()
        for topic_name in new_topics:
            topic = self.db.query(Topic).filter(Topic.topic_name == topic_name).first()
            if topic:
                user_topic = UserTopic(user_id=user_id, topic_id=topic.topic_id)
                self.db.add(user_topic)
        self.db.commit()

    def remove_topic_from_user(self, user_id: int, topic_name: str) -> None:
        db_user = self.user_repo.find_by_id(user_id)
        if db_user:
            topic = self.db.query(UserTopic).filter(UserTopic.user_id == user_id, UserTopic.topic_name == topic_name).first()
            if topic:
                db_user.user_topics.remove(topic)
                self.db.commit()

    def get_user_topics(self, user_id: int) -> list:
        db_user = self.user_repo.find_by_id(user_id)
        if db_user:
            return db_user.topics
        return []