from typing import List, Optional
from sqlalchemy.orm import Session
from typing import Sequence

# from app.schema.topic import Topic
from app.utils.logger import log_decorator
from app.schema.user import User, UserCreate, UserBase
from app.schema.user_topic import UserTopicBase
from app.data_access.repositories.user_repository import UserRepository
from app.schema.user_assessment import UserAssessmentCreate, UserAssessmentBase
from app.data_access.models.user import User as DBUser, UserAssessment, UserTopic
from app.data_access.models.topic import Topic
from app.schema.authentication import AuthenticationRequest, AuthenticationResponse

import bcrypt

from app.services.language_service import LanguageService
from datetime import date, datetime

class UserService:
    @log_decorator
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.language_service = LanguageService(db)

    # hashes a password
    def hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        salted_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return salted_hash.decode('utf-8')
    
    # verifies a password hash 
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)

    @log_decorator
    def create_user(self, user_create: UserCreate) -> User:
        hashed_password = self.hash_password(user_create.password_hash)

        db_user = DBUser(
            username=user_create.username.lower(), # convert username to lowercase
            email=user_create.email,
            password_hash=hashed_password, # use the hashed password 
            user_type=user_create.user_type,
            base_language=user_create.base_language,
            learning_languages=user_create.learning_languages,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            preferred_name=user_create.preferred_name,
            age=user_create.age,
            gender=user_create.gender,
            discovery_method=user_create.discovery_method,
            motivation=user_create.motivation,
            middle_name=user_create.middle_name,
            mobile_phone=user_create.mobile_phone,
            landline_phone=user_create.landline_phone,
            contact_preference=user_create.contact_preference,
            enrollment_date=datetime.today().date() # set enrollment date to today 
        )
        self.db.add(db_user)
        
        self.db.flush() # flush to get the db_user.id for FK relationships without committing the transaction
        
        # create initial default assessments (don't know if starter quizzes should replace this)
        if user_create.learning_languages:
            for language_name in user_create.learning_languages:
                language_schema = self.language_service.get_language_by_name(language_name=language_name)
                if language_schema:
                    default_assessment = UserAssessment(
                        user_id=db_user.user_id,
                        assessment_date=date.today(),
                        assessment_type="Initial",
                        skill_level="beginner",
                        language_id=language_schema.language_id,
                    )
                    self.db.add(default_assessment)
            
        self.db.commit()
        self.db.refresh(db_user)  # Refresh the db_user object after committing to get the user_id

        if user_create.user_topics:
            #db_user.user_topics = 
            self.add_user_topics(db_user, user_create.user_topics)

        return db_user
    


    def add_user_topics(self, db_user: User, topics: List[UserTopicBase]) -> None:
        # Create UserTopic objects
        user_topics = []
        for topic_base in topics:
            user_topic = UserTopic(topic_name=topic_base.topic_name, user_id=db_user.user_id, user=db_user)
            user_topics.append(user_topic)

        # Add UserTopic objects to session and commit
        self.db.add_all(user_topics)
        self.db.commit()
        #self.db.refresh(user_topics)  # Refresh the user_topics objects after committing to get any changes from the database
        



    @log_decorator
    def get_user_by_id(self, user_id: int) -> User:
        db_user = self.user_repo.find_by_id(user_id)
        return db_user

    @log_decorator
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.user_repo.find_by_username(username.lower())

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
    def update_user_topics(self, username: str, new_topics: User) -> None:
        user = self.db.query(DBUser).filter(DBUser.username == username.lower()).first()
        
        # Checking if user exists
        if user:
            # Deleting UserTopics associated with the found user_id
            self.db.query(UserTopic).filter(UserTopic.user_id == user.user_id).delete()
            for topic_base in new_topics.user_topics:
                topic = self.db.query(Topic).filter(Topic.topic_name == topic_base.topic_name).first()
                if topic:
                    user_topic = UserTopic(user_id=user.user_id, topic_name=topic.topic_name)
                    self.db.add(user_topic)
            self.db.commit()
            print("UserTopics updated for user:", username)
        else:
            print("User not found with username:", username)

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
        db_user = self.user_repo.find_by_username(request.username.lower())

        if not db_user:
            return AuthenticationResponse.failure(
                message="No matching user found, please register"
            )
        if not self.verify_password(request.password, db_user.password_hash):
            return AuthenticationResponse.failure(
                message="Incorrect username or password."
            )

        today = datetime.today().date()
        if db_user.last_login_date:
            if today == db_user.last_login_date:
                # user has already logged in today
                pass
            elif (today - db_user.last_login_date).days == 1:
                # consecutive login
                db_user.consecutive_login_days += 1
            else:
                # not consecutive login => reset counter
                db_user.consecutive_login_days = 1
        else:
            db_user.consecutive_login_days = 1 # user first login
        db_user.last_login_date = today # update last login day
        self.db.commit()
        return AuthenticationResponse.success(username=request.username)
    
    def create_user_assessment(self, user_id: int, assessment_data: UserAssessmentCreate) -> UserAssessment:
        db_assessment = UserAssessment(
            user_id=user_id,
            assessment_date=assessment_data.assessment_date,
            assessment_type=assessment_data.assessment_type,
            skill_level=assessment_data.skill_level,
            strength=assessment_data.strength,
            weakness=assessment_data.weakness,
            language_id=assessment_data.language_id,
        )
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

    @log_decorator
    def update_user_languages(self, username: str, user: User):
        db_user = self.db.query(DBUser).filter(DBUser.username == username).first()
        if db_user:
            # get current languages 
            current_languages = set(db_user.learning_languages)
            new_languages = set(user.learning_languages)
            # determine the newly added languages
            added_languages = new_languages - current_languages
            # update learning languages
            db_user.learning_languages = user.learning_languages
            # add initial assessments for the newly added languages 
            for language_name in added_languages:
                language_schema = self.language_service.get_language_by_name(language_name)
                if language_schema:
                    existing_assessment = (
                        self.db.query(UserAssessment)
                        .filter(UserAssessment.user_id == db_user.user_id,
                                UserAssessment.language_id == language_schema.language_id)
                        .first()
                    )
                    if not existing_assessment:
                        default_assessment = UserAssessment(
                            user_id=db_user.user_id,
                            assessment_date=date.today(),
                            assessment_type="Initial",
                            skill_level="beginner",
                            language_id=language_schema.language_id,
                        )
                        self.db.add(default_assessment)
            self.db.commit()
            
    @log_decorator
    def update_user_profile(self, username: str, user_update: UserCreate) -> User:
        db_user = self.db.query(DBUser).filter(DBUser.username == username).first()
        if not db_user:
            raise ValueError("user not found")
        # update fields 
        db_user.first_name = user_update.first_name
        db_user.middle_name = user_update.middle_name
        db_user.last_name = user_update.last_name
        db_user.preferred_name = user_update.preferred_name
        db_user.base_language = user_update.base_language
        db_user.gender = user_update.gender
        db_user.email = user_update.email
        db_user.mobile_phone = user_update.mobile_phone
        db_user.contact_preference = user_update.contact_preference
        
        self.db.commit()
        return db_user

    @log_decorator
    def change_password(self, username: str, current_password: str, new_password: str):
        db_user = self.db.query(DBUser).filter(DBUser.username == username).first()
        if not db_user or not self.verify_password(current_password, db_user.password_hash):
            raise ValueError("Current password is incorrect")
        db_user.password_hash = self.hash_password(new_password)
        self.db.commit()