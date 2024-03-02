from datetime import date

from .base_repository import BaseRepository
from sqlalchemy.orm import Session
from typing import Optional
from typing import List

from app.models.data_models.user import User
from datetime import date


class UserRepository(BaseRepository[User]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, User)

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self.db_session.query(User).filter(User.user_id == user_id).first()

    def find_by_username(self, username: str) -> Optional[User]:
        return self.db_session.query(User).filter(User.username == username).first()

    def get_all_users(self) -> List[User]:
        return self.db_session.query(User).all()