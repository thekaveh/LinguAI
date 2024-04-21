from sqlmodel import Session
from typing import AsyncIterable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.messages import HumanMessage, SystemMessage

from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.models.embeddings_quiz import (
    EmbeddingsQuizRequest,
    EmbeddingsQuizResponse,
)


class EmbeddingsQuizService:
    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @log_decorator
    async def agenerate(self, request: EmbeddingsQuizRequest) -> EmbeddingsQuizResponse:
        assert request is not None, "message is required"
        assert request.llm_id is not None, "llm_id is required"
        assert request.llm_temperature is not None, "llm_temperature is required"
        assert request.src_lang is not None, "src_lang is required"
        assert request.dst_lang is not None, "dst_lang is required"
        assert request.difficulty is not None, "difficulty is required"

        return EmbeddingsQuizResponse(
            src_lang=request.src_lang,
            dst_lang=request.dst_lang,
            difficulty=request.difficulty,
            src_lang_question="Hello!",
            dst_lang_question="And Goodbye!",
        )
