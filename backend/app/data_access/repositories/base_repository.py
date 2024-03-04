from sqlalchemy.orm import Session
from typing import Generic, TypeVar, Type, List, Optional

from app.utils.logger import log_decorator

T = TypeVar("T")


class BaseRepository(Generic[T]):
    @log_decorator
    def __init__(self, db_session: Session, model_type: Type[T]):
        self.db_session = db_session
        self.model_type = model_type

    @log_decorator
    def create(self, create_schema) -> T:
        db_item = self.model_type(**create_schema.dict())
        self.db_session.add(db_item)
        self.db_session.commit()
        self.db_session.refresh(db_item)
        return db_item

    @log_decorator
    def get_by_id(self, id: int) -> Optional[T]:
        return self.db_session.query(self.model_type).get(id)

    @log_decorator
    def get_all(self) -> List[T]:
        return self.db_session.query(self.model_type).all()

    @log_decorator
    def remove(self, id: int) -> None:
        db_item = self.db_session.query(self.model_type).get(id)
        if db_item:
            self.db_session.delete(db_item)
            self.db_session.commit()