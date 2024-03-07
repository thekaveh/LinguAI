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
        return self.persona_repository.create(create).to_schema()

    @log_decorator
    def update(self, id: int, update: PersonaUpdate) -> Optional[Persona]:
        current = self.persona_repository.get_by_id(id)

        if current is None:
            return None

        return self.persona_repository.update(current, update).to_schema()

    @log_decorator
    def delete(self, id: int) -> None:
        self.persona_repository.delete(id)

    @log_decorator
    def get_by_id(self, id: int) -> Optional[Persona]:
        ret = self.persona_repository.get_by_id(id)

        return ret.to_schema() if ret else None

    @log_decorator
    def get_by_criteria(self, criteria: PersonaSearch) -> Optional[Persona]:
        ret = self.persona_repository.get_by_criteria(criteria)

        return ret.to_schema() if ret else None

    @log_decorator
    def get_all(self) -> List[Persona]:
        return [model.to_schema() for model in self.persona_repository.get_all()]
