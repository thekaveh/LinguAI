from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import Generic, TypeVar, Type, List, Optional

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, db_session: Session, model_type: Type[T]):
        self.db_session = db_session
        self.model_type = model_type

    def create(self, create_schema) -> T:
        db_item = self.model_type(**create_schema.dict())
        self.db_session.add(db_item)
        self.db_session.commit()
        self.db_session.refresh(db_item)
        return db_item

    def get_by_id(self, id: int) -> Optional[T]:
        return self.db_session.query(self.model_type).get(id)

    def get_all(self) -> List[T]:
        return self.db_session.query(self.model_type).all()

    def remove(self, id: int) -> None:
        db_item = self.db_session.query(self.model_type).get(id)
        if db_item:
            self.db_session.delete(db_item)
            self.db_session.commit()