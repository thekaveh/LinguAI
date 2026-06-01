from __future__ import annotations
from pydantic import BaseModel, Field


class Persona(BaseModel):
    persona_id: int = Field(...)
    persona_name: str = Field(...)
    description: str = Field(...)
    is_default: bool = Field(default=False)
