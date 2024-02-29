from sqlalchemy.orm import Session
from app.models.data_models.user import User as DBUser
from app.models.schema.user import User, UserCreate

class UserService:
    def __init__(self, db: Session):
        self.db = db

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
        db_user = self.db.query(DBUser).filter(DBUser.user_id == user_id).first()
        return db_user

    def get_users(self) -> list:
        return self.db.query(DBUser).all()
