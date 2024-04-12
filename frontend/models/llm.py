import os
from sqlmodel import SQLModel, Field

is_backend = os.getenv("APP_CONTEXT") == "backend"


class LLM(SQLModel, table=is_backend):
    id: int = Field(primary_key=True)
    is_active: bool = Field(default=False)
    vision: int = Field(default=-1)
    content: int = Field(default=-1)
    embeddings: int = Field(default=-1)
    provider: str = Field(nullable=False)
    name: str = Field(max_length=100, nullable=False)

    def display_name(self) -> str:
        return f"{self.name}   |   {self.provider}"
