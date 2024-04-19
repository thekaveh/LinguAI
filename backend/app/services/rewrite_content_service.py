from typing import AsyncIterable
from sqlalchemy.orm import Session
from sqlmodel import Session as SqlModelSession
from langchain.schema.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.utils.logger import log_decorator
from app.schema.prompt import PromptSearch
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.schema.rewrite_content import ContentRewriteReq


class RewriteContentService:
    @log_decorator
    def __init__(self, db: Session, sql_model_session: SqlModelSession):
        self.db = db
        self.prompt_service = PromptService(db)
        self.sql_model_session = sql_model_session

    @log_decorator
    async def arewrite_content(self, request: ContentRewriteReq) -> AsyncIterable[str]:
        """
        Rewrites the content based on the given request.

        Args:
            request (ContentRewriteReq): The request object containing the necessary information for content rewriting.

        Returns:
            AsyncIterable[str]: An asynchronous iterable that yields the rewritten content.

        Raises:
            AssertionError: If the request is None.
        """
        assert request is not None, "Request is required"

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
        """
        Generate a prompt for content rewriting based on the user's request.

        Args:
            request (ContentRewriteReq): The user's request for content rewriting.

        Returns:
            str: The generated prompt for content rewriting.
        """
        feedback_lang = request.user_base_language
        skill_level = request.user_skill_level
        if skill_level:
            feedback_lang = request.language
        else:
            skill_level = "beginner"

        # Define the search criteria
        search_criteria = PromptSearch(
            prompt_type="system", prompt_category="rewrite-content-by-skill-level"
        )
        # Fetch the prompt based on the defined criteria
        db_prompt = self.prompt_service.get_prompt_by_search_criteria(search_criteria)

        if db_prompt:
            # Assuming the prompt text in the database is a template that needs to be formatted
            return f""" You will RE-WRITE the following {request.language} input content 
                        for a reader at {request.skill_level} skill level in the same {request.language}. 

                        \n Provide feedback on what you changed in a separate section. 
                        Your feedback should be in {feedback_lang} language for a reader at {skill_level} skill level.

                        \n Below is the input content:

                        {request.input_content}
                    """
        else:
            # Handle cases where no matching prompt is found
            return f""" You will RE-WRITE the following {request.language} input content 
                        for a reader at {request.skill_level} skill level in the same {request.language}. 

                        \n Provide feedback on what you changed in a separate section. 
                        Your feedback should be in {feedback_lang} language for a reader at {skill_level} skill level.

                        \n Below is the input content:

                        {request.input_content}
                    """
