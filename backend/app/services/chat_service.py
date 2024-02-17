from typing import AsyncIterable, List, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.services.llm_service import LLMService
from app.services.persona_service import PersonaService

class ChatService:
    @staticmethod
    async def achat(
        messages		: List[Tuple[str, str]]
        , model			: str
        , temperature	: float = 0
        , persona		: str = "Neutral"
    ) -> AsyncIterable[str]:
        messages = ChatPromptTemplate.from_messages([("system", PersonaService.get_persona(persona).description)] + messages)
        llm = LLMService.get_runnable(model=model, temperature=temperature)
        parser = StrOutputParser()
        
        chain = messages | llm | parser
        
        return chain.astream(input={})
        
        # return (
        #     chunk async for chunk in chain.astream({})
        # )
