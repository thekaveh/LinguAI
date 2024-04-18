from typing import List
from sqlmodel import SQLModel, Field


class EmbeddingsQuizRequest(SQLModel, table=False):
    llm_id: int = Field(nullable=False)
    llm_temperature: float = Field(nullable=False, default=0.0)

    source_lang: str = Field(nullable=False, default="English")
    target_lang: str = Field(nullable=False)
    difficulty: str = Field(nullable=False, default="easy")


class EmbeddingsQuizResponse(SQLModel, table=False):
    source_lang: str = Field(nullable=False, default="English")
    target_lang: str = Field(nullable=False)
    difficulty: str = Field(nullable=False, default="easy")

    source_question: str = Field(nullable=False)
    target_question: str = Field(nullable=False)
