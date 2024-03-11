from typing import Optional
from sqlalchemy.orm import Session

from app.schema.topic import Topic
from app.utils.logger import log_decorator
from app.schema.user import User, UserCreate
from app.schema.user_topic import UserTopicBase
from app.data_access.repositories.user_repository import UserRepository
from app.schema.user_assessment import UserAssessmentCreate, UserAssessmentBase
from app.data_access.models.user import User as DBUser, UserAssessment, UserTopic
from app.schema.authentication import AuthenticationRequest, AuthenticationResponse


class UserService:
    @log_decorator
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    @log_decorator
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
            contact_preference=user_create.contact_preference,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    @log_decorator
    def get_user_by_id(self, user_id: int) -> User:
        db_user = self.user_repo.find_by_id(user_id)
        return db_user

    @log_decorator
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.user_repo.find_by_username(username)

    @log_decorator
    def get_users(self) -> list:
        return self.user_repo.get_all_users()

    @log_decorator
    def add_topic_to_user(self, user_id: int, topic_name: str) -> None:
        db_user = self.user_repo.find_by_id(user_id)
        if db_user:
            topic = (
                self.db.query(UserTopic)
                .filter(
                    UserTopic.user_id == user_id, UserTopic.topic_name == topic_name
                )
                .first()
            )
            if topic:
                db_user.user_topics.append(topic)
                self.db.commit()

    @log_decorator
    def update_user_topics(self, user_id: int, new_topics: list) -> None:
        self.db.query(UserTopic).filter(UserTopic.user_id == user_id).delete()
        for topic_name in new_topics:
            topic = self.db.query(Topic).filter(Topic.topic_name == topic_name).first()
            if topic:
                user_topic = UserTopic(user_id=user_id, topic_id=topic.topic_id)
                self.db.add(user_topic)
        self.db.commit()

    @log_decorator
    def remove_topic_from_user(self, user_id: int, topic_name: str) -> None:
        db_user = self.user_repo.find_by_id(user_id)
        if db_user:
            topic = (
                self.db.query(UserTopic)
                .filter(
                    UserTopic.user_id == user_id, UserTopic.topic_name == topic_name
                )
                .first()
            )
            if topic:
                db_user.user_topics.remove(topic)
                self.db.commit()

    @log_decorator
    def get_user_topics(self, user_id: int) -> list:
        db_user = self.user_repo.find_by_id(user_id)
        if db_user:
            return db_user.topics
        return []

    @log_decorator
    def authenticate(self, request: AuthenticationRequest) -> AuthenticationResponse:
        db_user = self.user_repo.find_by_username(request.username)

        if not db_user:
            return AuthenticationResponse.failure(
                message="No matching user found, please register"
            )
        if db_user.password_hash != request.password:
            return AuthenticationResponse.failure(
                message="Incorrect username or password."
            )

        return AuthenticationResponse.success(username=request.username)

    def create_user_assessment(
        self, user_id: int, assessment_data: UserAssessmentCreate
    ) -> UserAssessment:
        db_assessment = UserAssessment(**assessment_data.dict(), user_id=user_id)
        self.db.add(db_assessment)
        self.db.commit()
        self.db.refresh(db_assessment)
        return db_assessment

    def get_user_assessment(self, assessment_id: int) -> Optional[UserAssessment]:
        return (
            self.db.query(UserAssessment)
            .filter(UserAssessment.assessment_id == assessment_id)
            .first()
        )

    def update_user_assessment(
        self, assessment_id: int, assessment_data: UserAssessmentCreate
    ) -> Optional[UserAssessment]:
        db_assessment = self.get_user_assessment(assessment_id)
        if db_assessment:
            for key, value in assessment_data.dict().items():
                setattr(db_assessment, key, value)
            self.db.commit()
            self.db.refresh(db_assessment)
            return db_assessment
        else:
            return None

    def delete_user_assessment(self, assessment_id: int) -> None:
        db_assessment = self.get_user_assessment(assessment_id)
        if db_assessment:
            self.db.delete(db_assessment)
            self.db.commit()
