from sqlmodel import SQLModel, Field


class PolyglotPuzzleRequest(SQLModel, table=False):
    llm_id: int = Field(nullable=False)
    llm_temperature: float = Field(nullable=False, default=0.0)

    src_lang: str = Field(nullable=False, default="English")
    dst_lang: str = Field(nullable=False)
    difficulty: str = Field(nullable=False, default="easy")


class PolyglotPuzzleResponse(SQLModel, table=False):
    src_lang_question: str = Field(nullable=False)
    dst_lang_question: str = Field(nullable=False)
