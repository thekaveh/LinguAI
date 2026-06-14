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
        """
        Creates a new item in the database.

        Args:
            create_schema: The schema containing the data for creating the item.

        Returns:
            The created item.

        """
        db_item = self.model_type(**create_schema.dict())
        self.db_session.add(db_item)
        self.db_session.commit()
        self.db_session.refresh(db_item)
        return db_item

    @log_decorator
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Retrieve an entity from the database by its ID.

        Args:
            id (int): The ID of the entity to retrieve.

        Returns:
            Optional[T]: The retrieved entity, or None if not found.
        """
        return self.db_session.query(self.model_type).get(id)

    @log_decorator
    def get_all(self) -> List[T]:
        """
        Retrieve all instances of the model from the database.

        Returns:
            A list of instances of the model.
        """
        return self.db_session.query(self.model_type).all()

    @log_decorator
    def remove(self, id: int) -> None:
        """
        Removes an item from the database based on its ID.

        Args:
            id (int): The ID of the item to be removed.

        Returns:
            None
        """
        db_item = self.db_session.query(self.model_type).get(id)
        if db_item:
            self.db_session.delete(db_item)
            self.db_session.commit()
