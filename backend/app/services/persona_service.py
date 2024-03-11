from typing import List, Optional
from sqlalchemy.orm import Session

from app.utils.logger import log_decorator
from app.data_access.repositories.persona_repository import PersonaRepository
from app.schema.persona import Persona, PersonaCreate, PersonaUpdate, PersonaSearch


class PersonaService:
    @log_decorator
    def __init__(self, db_session: Session):
        self.persona_repository = PersonaRepository(db_session)

    @log_decorator
    def create(self, create: PersonaCreate) -> Persona:
        persona_orm = self.persona_repository.create(create)
        
        return Persona.model_validate(persona_orm)

    @log_decorator
    def update(self, id: int, update: PersonaUpdate) -> Optional[Persona]:
        current_persona_orm = self.persona_repository.get_by_id(id)

        if current_persona_orm is None:
            return None

        updated_persona_orm = self.persona_repository.update(current_persona_orm, update)
        
        return Persona.model_validate(updated_persona_orm)

    @log_decorator
    def delete(self, id: int) -> None:
        self.persona_repository.delete(id)

    @log_decorator
    def get_by_id(self, id: int) -> Optional[Persona]:
        persona_orm = self.persona_repository.get_by_id(id)
        
        return Persona.model_validate(persona_orm) if persona_orm else None

    @log_decorator
    def get_by_criteria(self, criteria: PersonaSearch) -> Optional[Persona]:
        persona_orm = self.persona_repository.get_by_criteria(criteria)

        return Persona.model_validate(persona_orm) if persona_orm else None

    @log_decorator
    def get_all(self) -> List[Persona]:
        return [Persona.model_validate(persona_orm) for persona_orm in self.persona_repository.get_all() if persona_orm]
