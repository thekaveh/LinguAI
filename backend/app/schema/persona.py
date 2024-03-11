from pydantic import BaseModel


class PersonaBase(BaseModel):
    persona_name: str
    description: str
    is_default: bool


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(PersonaBase):
    pass


class Persona(PersonaBase):
    persona_id: int

    class Config:
        from_attributes = True


class PersonaSearch(BaseModel):
    persona_name: str
