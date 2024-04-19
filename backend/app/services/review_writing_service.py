from typing import AsyncIterable
from sqlalchemy.orm import Session
from sqlmodel import Session as SqlModelSession
from langchain.schema.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.schema.prompt import PromptSearch
from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.schema.review_writing import ReviewWritingReq
from app.services.skill_level_service import SkillLevelService


class ReviewWritingService:
    @log_decorator
    def __init__(self, db: Session, sql_model_session: SqlModelSession):
        self.db = db
        self.prompt_service = PromptService(db)
        self.sql_model_session = sql_model_session
        self.skill_level_service = SkillLevelService(db)

    @log_decorator
    async def areview_writing(self, request: ReviewWritingReq) -> AsyncIterable[str]:
        """
        Generates a review based on the given request.

        Args:
            request (ReviewWritingReq): The request object containing the necessary information.

        Returns:
            AsyncIterable[str]: An asynchronous iterable that yields the generated review.

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
    def _generate_prompt(self, request: ReviewWritingReq) -> str:
        """
        Generates a prompt for reviewing input content based on the writer's skill level and language.

        Args:
            request (ReviewWritingReq): The request object containing information about the writer's skill level, language, and input content.

        Returns:
            str: The generated prompt for reviewing the input content.

        Raises:
            None
        """
        # Define the search criteria
        search_criteria = PromptSearch(
            prompt_type="system", prompt_category="rewrite-content-by-skill-level"
        )
        # Fetch the prompt based on the defined criteria
        db_prompt = self.prompt_service.get_prompt_by_search_criteria(search_criteria)

        # The last feedback provided as strengths is {request.strength} and the weakness is {request.weakness}.

        if db_prompt:
            # Assuming the prompt text in the database is a template that needs to be formatted
            return f"""
                    The writer of the following text is currently at {request.curr_skill_level} skill level in {request.language} language. 
                    The next skill level for the writter is {request.next_skill_level} level. 
                    The last feedback provided as strengths is {request.strength} and the weakness is {request.weakness}.
                    
                    \n With the above information, now review the following input content from the writer below and provide summary of findings, 
                    and provide feedback in DIRECT VOICE to improve from {request.curr_skill_level.upper} skill level to next. 
                    
                    \n Your feedback should be in  {request.language}
                    
                    \nHere is the input content to review:
                    
                    {request.input_content}
                    
                    """

        else:
            # Handle cases where no matching prompt is found
            # Assuming the prompt text in the database is a template that needs to be formatted
            return f"""
                    The writer of the following text is currently at {request.curr_skill_level.upper} skill level in language {request.language.upper}. 
                    The next skill level for the writter is {request.next_skill_level.upper}. 
                    
                    \n With the above information, now review the following input content from the writer below and provide summary of findings, 
                    and provide feedback in DIRECT VOICE to improve from {request.curr_skill_level.upper} skill level to next. 
                    
                    \n Your feedback should be in  {request.language.upper} language.
                    
                    \nHere is the input content to review:
                    
                    {request.input_content}
                    
                    """
