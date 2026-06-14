from typing import List, Optional
from sqlmodel import Session, select

from app.models.persona import Persona
from app.utils.logger import log_decorator
from app.services.crud_service import CRUDService


class PersonaService(CRUDService[Persona]):
    """
    Service class for managing Persona objects in the database.
    """

    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @log_decorator
    def get_all(self) -> List[Persona]:
        personas = self.db_session.exec(select(Persona)).all()

        return personas

    @log_decorator
    def get_by_id(self, id: int) -> Optional[Persona]:
        persona = self.db_session.get(Persona, id)

        return persona

    @log_decorator
    def get_by_name(self, name: str) -> Optional[Persona]:
        """
        Retrieves a Persona object from the database based on the given name.

        Args:
            name (str): The name of the persona to retrieve.

        Returns:
            Optional[Persona]: The Persona object if found, None otherwise.
        """
        query = select(Persona).where(Persona.persona_name == name)

        return self.db_session.exec(query).first()

    @log_decorator
    def create(self, entity: Persona) -> Persona:
        """
        Creates a new persona in the database.

        Args:
            entity (Persona): The persona object to be created.

        Returns:
            Persona: The created persona object.
        """
        self.db_session.add(entity)
        self.db_session.commit()
        self.db_session.refresh(entity)

        return entity

    @log_decorator
    def update(self, id: int, value: Persona) -> Optional[Persona]:
        """
        Update a persona with the given ID.

        Args:
            id (int): The ID of the persona to update.
            value (Persona): The updated persona data.

        Returns:
            Optional[Persona]: The updated persona if found, None otherwise.
        """
        persona = self.db_session.get(Persona, id)

        if not persona:
            return None

        data = value.dict(exclude_unset=True)

        for key, value in data.items():
            setattr(persona, key, value)

        self.db_session.add(persona)
        self.db_session.commit()
        self.db_session.refresh(persona)

        return persona

    @log_decorator
    def delete(self, id: int) -> None:
        """
        Deletes a persona from the database.

        Args:
            id (int): The ID of the persona to delete.

        Returns:
            None
        """
        persona = self.db_session.get(Persona, id)

        if persona:
            self.db_session.delete(persona)
            self.db_session.commit()
