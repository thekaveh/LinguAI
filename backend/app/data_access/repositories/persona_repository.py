from typing import List, Optional
from sqlalchemy.orm import Session

from app.utils.logger import log_decorator
from app.data_access.models.persona import Persona
from app.schema.persona import PersonaCreate, PersonaUpdate, PersonaSearch


class PersonaRepository:
    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @log_decorator
    def get_by_id(self, id: int) -> Optional[Persona]:
        return self.db_session.query(Persona).filter(Persona.persona_id == id).first()

    @log_decorator
    def get_by_criteria(self, criteria: PersonaSearch) -> Optional[Persona]:
        return (
            self.db_session.query(Persona)
            .filter(
                Persona.persona_name == criteria.persona_name,
            )
            .first()
        )

    @log_decorator
    def get_all(self) -> List[Persona]:
        return self.db_session.query(Persona).all()

    @log_decorator
    def create(self, create: PersonaCreate) -> Persona:
        new_persona = Persona(
            persona_name=create.persona_name,
            description=create.description,
        )

        self.db_session.add(new_persona)
        self.db_session.commit()
        self.db_session.refresh(new_persona)

        return new_persona

    @log_decorator
    def update(self, persona: Persona, update: PersonaUpdate) -> Persona:
        update_data = update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(persona, key, value)

        self.db_session.commit()
        self.db_session.refresh(persona)

        return persona

    @log_decorator
    def delete(self, id: int) -> None:
        persona = self.get_by_id(id)

        if persona:
            self.db_session.delete(persona)
            self.db_session.commit()
