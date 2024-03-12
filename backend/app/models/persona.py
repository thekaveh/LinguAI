from sqlmodel import SQLModel, Field

class Persona(SQLModel, table=True):
    persona_id: int = Field(primary_key=True, alias="persona_id")
    persona_name: str = Field(max_length=100, nullable=False, alias="persona_name")
    description: str = Field(nullable=False, alias="description")
    is_default: bool = Field(default=False, alias="is_default")