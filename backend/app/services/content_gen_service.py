from typing import AsyncIterable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.messages import SystemMessage, HumanMessage
from app.services.llm_service import LLMService
from app.models.schema.content_gen import ContentGenReq
from app.models.schema.prompt import PromptSearch
from app.core.config import Config
from app.services.prompt_service import PromptService
from sqlalchemy.orm import Session
from app.repositories.prompt_repository import PromptRepository


class ContentGenService:
    def __init__(self, db: Session):
        self.db = db
        self.prompt_service = PromptService(db)    

    async def generate_content(self,request: ContentGenReq) -> AsyncIterable[str]:
        assert request is not None, "Request is required"
        
        prompt_text = self.generate_prompt(request)
        

        system_message = SystemMessage(content=prompt_text)
        prompt = ChatPromptTemplate.from_messages([system_message])
        
        # Use temperature from the request if provided, else use the default
        temperature = float(Config.DEFAULT_TEMPERATURE)

        chat_runnable = LLMService.get_chat_runnable(
            model=Config.DEFAULT_LANGUAGE_TRANSLATION_MODEL,
            temperature=temperature
        )
        parser = StrOutputParser()
        chain = prompt | chat_runnable | parser

        async for generated_content in chain.astream(input={}):
            yield generated_content


    def generate_prompt(self,request: ContentGenReq) -> str:
        # Define the search criteria
        search_criteria = PromptSearch(
            prompt_type="system",
            prompt_category="content-gen-by-topics-content"
        )
        # Fetch the prompt based on the defined criteria
        db_prompt = self.prompt_service.get_prompt_by_search_criteria(search_criteria)
        
        if db_prompt:
            # Assuming the prompt text in the database is a template that needs to be formatted
            formatted_prompt = db_prompt.prompt_text.format(
                content_name=request.content.content_name,
                topics=', '.join(request.user_topics),
                language_name=request.language.language_name
            )
            return formatted_prompt
        else:
            # Handle cases where no matching prompt is found
            return f"""Generate a {request.content.content_name} for the following topics: {', '.join(request.user_topics)}. 
                       Content should be generated only in {request.language.language_name} language."""
