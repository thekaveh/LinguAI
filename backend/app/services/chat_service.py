from typing import AsyncIterable
from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.messages import HumanMessage, SystemMessage

from app.schema.chat import ChatRequest
from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.schema.persona import Persona, PersonaSearch
from app.services.persona_service import PersonaService


class ChatService:
    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @log_decorator
    async def achat(self, request: ChatRequest) -> AsyncIterable[str]:
        assert request is not None, "message is required"
        assert request.model is not None, "model is required"
        assert request.messages is not None, "messages is required"
        assert len(request.messages) > 0, "messages must not be empty"

        persona_service = PersonaService(self.db_session)
        persona = persona_service.get_by_criteria(
            criteria=PersonaSearch(persona_name=request.persona)
        )
        print(persona if persona else "persona not found")
        if persona is None:
            raise ValueError("Persona not found")

        chat_messages = [SystemMessage(content=persona.description)] + [
            message.text for message in request.messages[:-1]
        ]

        chat_messages.append(HumanMessage(content=request.messages[-1].to_dict()))

        prompt = ChatPromptTemplate.from_messages(chat_messages)

        chat_runnable = LLMService.get_chat_runnable(
            model=request.model, temperature=request.temperature
        )
        parser = StrOutputParser()

        chain = prompt | chat_runnable | parser

        return chain.astream(input={})
