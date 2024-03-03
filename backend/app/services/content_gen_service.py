from typing import AsyncIterable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.messages import SystemMessage, HumanMessage
from app.services.llm_service import LLMService
from app.models.schema.content_gen import ContentGenReq
from app.services.persona_service import PersonaService
from app.core.config import Config

class ContentGenService:
    @staticmethod
    async def generate_content(request: ContentGenReq) -> AsyncIterable[str]:
        assert request is not None, "Request is required"
        
        prompt_text = ContentGenService.generate_prompt(request)
        system_message = SystemMessage(content=prompt_text)
        prompt = ChatPromptTemplate.from_messages([system_message])
        
        # Use temperature from the request if provided, else use default
        temperature = float(Config.DEFAULT_TEMPERATURE)

        chat_runnable = LLMService.get_chat_runnable(
            model=Config.DEFAULT_LANGUAGE_TRANSLATION_MODEL,
            temperature=temperature
        )
        parser = StrOutputParser()
        chain = prompt | chat_runnable | parser

        async for generated_content in chain.astream(input={}):
            yield generated_content


    @staticmethod
    def generate_prompt(request: ContentGenReq) -> str:
        # Generate prompt based on the request
        prompt = f"Generate a {request.content.content_name} for the following topics: {', '.join(request.user_topics)}."
        prompt += f"Content should be generated only in {request.language.language_name} language."
        return prompt
