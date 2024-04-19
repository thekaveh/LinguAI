from sqlmodel import SQLModel, Session
from typing import List, Optional, TypeVar, Protocol, Generic


T = TypeVar("T", bound=SQLModel)


class CRUDService(Protocol, Generic[T]):
    """
    A generic CRUD service interface for performing basic CRUD operations on entities.

    :param db_session: The database session to use for performing the operations.
    """

    db_session: Session

    def get_all(self) -> List[T]:
        """
        Retrieve all entities from the database.

        :return: A list of entities.
        """

    def get_by_id(self, id: int) -> Optional[T]:
        """
        Retrieve an entity by its ID from the database.

        :param id: The ID of the entity to retrieve.
        :return: The retrieved entity, or None if not found.
        """

    def create(self, entity: T) -> T:
        """
        Create a new entity in the database.

        :param entity: The entity to create.
        :return: The created entity.
        """

    def update(self, id: int, value: T) -> Optional[T]:
        """
        Update an existing entity in the database.

        :param id: The ID of the entity to update.
        :param value: The updated value of the entity.
        :return: The updated entity, or None if not found.
        """

    def delete(self, id: int) -> None:
        """
        Delete an entity from the database.

        :param id: The ID of the entity to delete.
        """
