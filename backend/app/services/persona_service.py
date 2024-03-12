from typing import List, Optional
from sqlmodel import Session, select

from app.models.persona import Persona
from app.utils.logger import log_decorator
from app.services.crud_service import CRUDService

class PersonaService(CRUDService[Persona]):
    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @log_decorator
    def get_by_id(self, id: int):
        persona = self.db_session.get(Persona, id)

        return persona

    @log_decorator
    def get_all(self) -> List[Persona]:
        personas = self.db_session.exec(select(Persona)).all()
        
        return personas

    @log_decorator
    def create(self, persona: Persona) -> Persona:
        self.db_session.add(persona)
        self.db_session.commit()
        self.db_session.refresh(persona)

        return persona

    @log_decorator
    def update(self, id: int, value: Persona) -> Optional[Persona]:
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
        persona = self.db_session.get(Persona, id)

        if persona:
            self.db_session.delete(persona)
            self.db_session.commit()
