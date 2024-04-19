import os
from sqlmodel import SQLModel, Field

is_backend = os.getenv("APP_CONTEXT") == "backend"


class Persona(SQLModel, table=is_backend):
    """
    Represents a persona in the application.

    Attributes:
        persona_id (int): The unique identifier for the persona.
        persona_name (str): The name of the persona.
        description (str): The description of the persona.
        is_default (bool): Indicates whether the persona is the default persona.
    """
    persona_id: int = Field(primary_key=True)
    persona_name: str = Field(max_length=100, nullable=False)
    description: str = Field(nullable=False)
    is_default: bool = Field(default=False)
