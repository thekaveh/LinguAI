from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

from app.schema.persona import Persona as PersonaSchema

Base = declarative_base()


class Persona(Base):
    __tablename__ = "persona"

    persona_id = Column(Integer, primary_key=True)
    persona_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    def to_schema(self) -> PersonaSchema:
        return PersonaSchema(
            persona_id=self.persona_id,
            persona_name=self.persona_name,
            description=self.description,
        )

    def __repr__(self):
        return f"<Persona(persona_id={self.persona_id}, persona_name='{self.persona_name}', description='{self.description}')>"
