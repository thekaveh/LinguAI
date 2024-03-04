from typing import AsyncIterable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.messages import HumanMessage, SystemMessage

from app.services.llm_service import LLMService
from app.models.common.chat_request import ChatRequest
from app.services.persona_service import PersonaService
from app.utils.logger import log_decorator


class ChatService:
    @log_decorator    
    @staticmethod
    async def achat(request: ChatRequest) -> AsyncIterable[str]:
        assert request is not None, "message is required"
        assert request.model is not None, "model is required"
        assert request.messages is not None, "messages is required"
        assert len(request.messages) > 0, "messages must not be empty"

        chat_messages = [
            SystemMessage(
                content=PersonaService.get_persona(request.persona).description
            )
        ] + [message.text for message in request.messages[:-1]]

        chat_messages.append(HumanMessage(content=request.messages[-1].to_dict()))

        prompt = ChatPromptTemplate.from_messages(chat_messages)

        chat_runnable = LLMService.get_chat_runnable(
            model=request.model, temperature=request.temperature
        )
        parser = StrOutputParser()

        chain = prompt | chat_runnable | parser

        return chain.astream(input={})
