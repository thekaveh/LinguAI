from sqlmodel import SQLModel, Session
from typing import List, Optional, TypeVar, Protocol, Generic


T = TypeVar("T", bound=SQLModel)

class CRUDService(Protocol, Generic[T]):
    db_session: Session

    def get_all(self) -> List[T]:
        ...

    def get_by_id(self, id: int) -> Optional[T]:
        ...

    def create(self, entity: T) -> T:
        ...

    def update(self, id: int, value: T) -> Optional[T]:
        ...

    def delete(self, id: int) -> None:
        ...