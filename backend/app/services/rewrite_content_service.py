from typing import AsyncIterable
from sqlalchemy.orm import Session
from langchain.schema.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import Config
from app.utils.logger import log_decorator
from app.schema.prompt import PromptSearch
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.schema.rewrite_content import ContentRewriteReq


class RewriteContentService:
    @log_decorator
    def __init__(self, db: Session):
        self.db = db
        self.prompt_service = PromptService(db)

    @log_decorator
    async def arewrite_content(self, request: ContentRewriteReq) -> AsyncIterable[str]:
        assert request is not None, "Request is required"

        prompt_text = self._generate_prompt(request)

        system_message = SystemMessage(content=prompt_text)
        prompt = ChatPromptTemplate.from_messages([system_message])

        # Use temperature from the request if provided, else use the default
        temperature = float(Config.DEFAULT_TEMPERATURE)

        chat_runnable = LLMService.get_chat_runnable(
            model=Config.DEFAULT_LANGUAGE_TRANSLATION_MODEL, temperature=temperature
        )
        parser = StrOutputParser()
        chain = prompt | chat_runnable | parser

        return chain.astream(input={})

    @log_decorator
    def _generate_prompt(self, request: ContentRewriteReq) -> str:
        # Define the search criteria
        search_criteria = PromptSearch(
            prompt_type="system", prompt_category="rewrite-content-by-skill-level"
        )
        # Fetch the prompt based on the defined criteria
        db_prompt = self.prompt_service.get_prompt_by_search_criteria(search_criteria)

        if db_prompt:
            # Assuming the prompt text in the database is a template that needs to be formatted
            return f""" You will RE-WRITE the following {request.language} input content 
                        for a reader at {request.skill_level} skill level in the same {request.language}, and provide feedback on what you changed. 
                        Below is the input content:

                        {request.input_content}
                    """
        else:
            # Handle cases where no matching prompt is found
            return f"""Rewrite the following input content {request.input_content} 
                    for language {request.language} at skill level {request.skill_level} 
                    in the same language  {request.language}. 
                    """
