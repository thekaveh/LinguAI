from pydantic import BaseModel


class PersonaBase(BaseModel):
    persona_name: str
    description: str


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(PersonaBase):
    pass


class Persona(PersonaBase):
    persona_id: int

    class Config:
        orm_mode = True


class PersonaSearch(BaseModel):
    persona_name: str
