import os
from sqlmodel import SQLModel, Field

is_backend = os.getenv("APP_CONTEXT") == "backend"


class Persona(SQLModel, table=is_backend):
    persona_id: int = Field(primary_key=True)
    persona_name: str = Field(max_length=100, nullable=False)
    description: str = Field(nullable=False)
    is_default: bool = Field(default=False)
