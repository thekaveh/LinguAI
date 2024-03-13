import os
from sqlmodel import SQLModel, Field

is_backend = os.getenv("APP_CONTEXT") == "backend"


class Language(SQLModel, table=is_backend):
    language_id: int = Field(primary_key=True)
    language_name: str = Field(max_length=255, nullable=False)
