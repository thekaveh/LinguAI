from typing import AsyncIterable, Optional
from sqlalchemy.orm import Session
from typing import AsyncIterable
from sqlalchemy.orm import Session
from langchain.schema.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.schema.review_writing import ReviewWritingReq
from app.schema.prompt import PromptSearch
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.utils.logger import log_decorator
from app.core.config import Config
from app.services.skill_level_service import SkillLevelService
from app.schema.skill_level import SkillLevelSchema

class ReviewWritingService:
    @log_decorator
    def __init__(self, db: Session):
        self.db = db
        self.prompt_service = PromptService(db)
        self.skill_level_service = SkillLevelService(db)

    @log_decorator
    async def review_writing(self, request: ReviewWritingReq) -> AsyncIterable[str]:
        assert request is not None, "Request is required"
            
        prompt_text = self.generate_prompt(request)

        
        system_message = SystemMessage(content=prompt_text)
        prompt = ChatPromptTemplate.from_messages([system_message])

        # Use temperature from the request if provided, else use the default
        temperature = float(Config.DEFAULT_TEMPERATURE)

        chat_runnable = LLMService.get_chat_runnable(
            model=Config.DEFAULT_LANGUAGE_TRANSLATION_MODEL, temperature=temperature
        )
        parser = StrOutputParser()
        chain = prompt | chat_runnable | parser

        async for generated_content in chain.astream(input={}):
            yield generated_content

    
    @log_decorator
    def generate_prompt(self, request: ReviewWritingReq) -> str:
        # Define the search criteria
        search_criteria = PromptSearch(
            prompt_type="system", prompt_category="rewrite-content-by-skill-level"
        )
        # Fetch the prompt based on the defined criteria
        db_prompt = self.prompt_service.get_prompt_by_search_criteria(search_criteria)

        if db_prompt:
            # Assuming the prompt text in the database is a template that needs to be formatted
            return f"""
                    The writer of the following text is currently at {request.curr_skill_level.upper} in language {request.language.upper}. 
                    The next skill level for the writter is {request.next_skill_level.upper}. 
                    The last feedback provided as strengths is {request.strength} and the weakness is {request.weakness}.
                    
                    With the above information, now review the following input content from the writer below and provide summary of findings, 
                    and provide feedback in DIRECT VOICE to improve further. Here is the input content to review:
                    
                    {request.input_content}
                    
                    """

        else:
            # Handle cases where no matching prompt is found
            return  f"""
                    The writer of the following text is currently at {request.curr_skill_level.upper} in language {request.language.upper}. 
                    The next skill level for the writter is {request.next_skill_level.upper}. 
                    The last feedback provided as strengths is {request.strength} and the weakness is {request.weakness}.
                    
                    With the above information, now review the following input content from the writer below and provide summary of findings, 
                    and provide feedback in DIRECT VOICE to improve further. Here is the input content to review:
                    
                    {request.input_content}
                    
                    """

