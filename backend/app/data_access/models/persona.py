from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean

from app.schema.persona import Persona as PersonaSchema

Base = declarative_base()


class Persona(Base):
    __tablename__ = "persona"

    persona_id = Column(Integer, primary_key=True)
    persona_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)

    def to_schema(self) -> PersonaSchema:
        return PersonaSchema(
            persona_id=self.persona_id,
            persona_name=self.persona_name,
            description=self.description,
            is_default=self.is_default,
        )

    def __repr__(self):
        return f"<Persona(persona_id={self.persona_id}, persona_name='{self.persona_name}', description='{self.description}')>"
