import os
from sqlmodel import SQLModel, Field

is_backend = os.getenv("APP_CONTEXT") == "backend"


class LLM(SQLModel, table=is_backend):
    id: int = Field(primary_key=True)
    is_active: bool = Field(default=False)
    is_default: bool = Field(default=False)
    is_vision: bool = Field(default=False)
    is_translate: bool = Field(default=False)
    name: str = Field(max_length=100, nullable=False)
    provider: str = Field(nullable=False)
