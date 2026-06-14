from typing import AsyncIterable
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlmodel import Session as SqlModelSession
from langchain.schema.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.schema.rewrite_content import ContentRewriteReq


class RewriteContentService:
    @log_decorator
    def __init__(self, db: Session, sql_model_session: SqlModelSession):
        self.db = db
        self.sql_model_session = sql_model_session

    @log_decorator
    async def arewrite_content(self, request: ContentRewriteReq) -> AsyncIterable[str]:
        """
        Rewrites the content based on the given request.
        """
        if request is None:
            raise HTTPException(status_code=422, detail="request body is required")

        prompt_text = self._generate_prompt(request)

        system_message = SystemMessage(content=prompt_text)
        prompt = ChatPromptTemplate.from_messages([system_message])

        chat_runnable = LLMService(db_session=self.sql_model_session).get_chat_runnable(
            llm_id=request.llm_id, temperature=request.temperature
        )
        parser = StrOutputParser()
        chain = prompt | chat_runnable | parser

        return chain.astream(input={})

    @log_decorator
    def _generate_prompt(self, request: ContentRewriteReq) -> str:
        """Build the system prompt for content rewriting.

        Collapsed from a dead if/db_prompt/else where both branches returned
        the same string. Moving prompt back into the DB requires a real
        template-substitution path; tracked as future work.
        """
        skill_level = request.user_skill_level or "beginner"
        feedback_lang = request.language if request.user_skill_level else request.user_base_language
        return (
            f"You will RE-WRITE the following {request.language} input content "
            f"for a reader at {request.skill_level} skill level in the same "
            f"{request.language}.\n\n"
            f"Provide feedback on what you changed in a separate section. "
            f"Your feedback should be in {feedback_lang} language for a reader "
            f"at {skill_level} skill level.\n\n"
            f"Below is the input content:\n\n{request.input_content}"
        )
