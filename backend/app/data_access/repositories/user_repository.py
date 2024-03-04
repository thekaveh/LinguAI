from typing import List, Optional
from sqlalchemy.orm import Session

from app.utils.logger import log_decorator
from app.data_access.models.user import User
from app.data_access.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    @log_decorator
    def __init__(self, db_session: Session):
        super().__init__(db_session, User)

    @log_decorator
    def find_by_id(self, user_id: int) -> Optional[User]:
        return self.db_session.query(User).filter(User.user_id == user_id).first()

    @log_decorator
    def find_by_username(self, username: str) -> Optional[User]:
        return self.db_session.query(User).filter(User.username == username).first()

    @log_decorator
    def get_all_users(self) -> List[User]:
        return self.db_session.query(User).all()
