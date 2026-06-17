from typing import AsyncIterable
from fastapi import HTTPException
from sqlmodel import Session as SqlModelSession
from langchain.schema.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.schema.review_writing import ReviewWritingReq


class ReviewWritingService:
    @log_decorator
    def __init__(self, sql_model_session: SqlModelSession):
        self.sql_model_session = sql_model_session

    @log_decorator
    async def areview_writing(self, request: ReviewWritingReq) -> AsyncIterable[str]:
        """
        Generates a review based on the given request.
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
    def _generate_prompt(self, request: ReviewWritingReq) -> str:
        """Build the system prompt for writing review.

        Collapsed from a dead if/db_prompt/else where both branches returned
        near-identical strings (and the truthy branch used ``str.upper`` —
        the method object, not the uppercased string — instead of ``.upper()``).
        Moving prompt back into the DB requires a real template path; tracked
        as future work.
        """
        skill = request.curr_skill_level.upper()
        next_skill = request.next_skill_level.upper()
        language = request.language.upper()
        return (
            f"The writer of the following text is currently at {skill} skill level "
            f"in {language} language. The next skill level for the writer is "
            f"{next_skill}. The last feedback noted strengths: {request.strength} "
            f"and weakness: {request.weakness}.\n\n"
            f"With the above information, review the following input content from "
            f"the writer and provide a summary of findings, plus feedback in "
            f"DIRECT VOICE to improve from {skill} to {next_skill}.\n\n"
            f"Your feedback should be in {language}.\n\n"
            f"Here is the input content to review:\n\n{request.input_content}"
        )
