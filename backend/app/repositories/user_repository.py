# user_repository.py
from .base_repository import BaseRepository
from sqlalchemy.orm import Session
from typing import List

# Import your User model
from app.models.data_models.user import User 

class UserRepository(BaseRepository[User]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, User)

    # Add any user-specific methods here
    def find_by_username(self, username: str) -> User:
        return self.db_session.query(User).filter(User.username == username).first()