from typing import AsyncIterable
from fastapi import HTTPException
from sqlmodel import Session as SqlModelSession
from langchain.schema.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.schema.content_gen import ContentGenReq


class ContentGenService:
    @log_decorator
    def __init__(self, sql_model_session: SqlModelSession):
        self.sql_model_session = sql_model_session


    async def agenerate_content(self, request: ContentGenReq) -> AsyncIterable[str]:
        """
        Generates content based on the given request.
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
    def _generate_prompt(self, request: ContentGenReq) -> str:
        """Build the system prompt for content generation.

        The previous implementation queried ``prompts`` for a DB-stored
        template but both branches returned the same hardcoded string, so
        the lookup was dead. Collapsed to the single template — moving the
        prompt back into the DB will require a real template-substitution
        path (PromptService + ``str.format``) and is tracked as future work.
        """
        topics = ", ".join(request.user_topics)
        return (
            f"Generate a {request.content.content_name} for a user at "
            f"{request.skill_level} reading skill level, for the following "
            f"topics: {topics}.\n\nContent should be generated only in "
            f"{request.language.language_name} language."
        )
