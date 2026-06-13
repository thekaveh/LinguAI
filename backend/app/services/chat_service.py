from sqlmodel import Session
from typing import AsyncIterable
from fastapi import HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage

from app.schema.chat import ChatMessage, ChatRequest
from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.services.persona_service import PersonaService
import logging
from app.core.config import Config


def _to_langchain_message(message: ChatMessage):
    """Translate a ChatMessage into the matching langchain message type.

    Assistant turns become AIMessage so the model sees its prior responses
    as its own — feeding them back as HumanMessage misleads the LLM about
    who said what.

    Image attachments are only emitted for the final user turn (the typical
    multimodal call shape). Earlier turns use plain text content; this avoids
    breaking providers like Groq/Ollama that don't accept the multimodal
    list-of-parts format.
    """
    if message.sender and message.sender.lower() in {"assistant", "ai", "bot"}:
        return AIMessage(content=message.text)
    return HumanMessage(content=message.text)


class ChatService:
    """
    Service class for handling chat functionality.
    """

    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger(Config.BACKEND_LOGGER_NAME)

    @log_decorator
    async def achat(self, request: ChatRequest) -> AsyncIterable[str]:
        """
        Performs a chat operation based on the given request.

        Args:
            request (ChatRequest): The chat request containing the necessary information.

        Returns:
            AsyncIterable[str]: An asynchronous iterable that yields the chat responses.

        Raises:
            HTTPException: 422 if the request body is malformed; 404 if the persona is unknown.

        """
        # `assert` is stripped under `python -O`; validate explicitly.
        if request is None or request.llm_id is None or not request.messages:
            raise HTTPException(status_code=422, detail="llm_id and at least one message are required")

        persona_service = PersonaService(self.db_session)
        llm_service = LLMService(self.db_session)

        persona = persona_service.get_by_name(name=request.persona)

        if persona is None:
            raise HTTPException(status_code=404, detail="Persona not found")

        chat_messages = [SystemMessage(content=persona.description)]
        chat_messages.extend(_to_langchain_message(m) for m in request.messages[:-1])

        # The final turn keeps its multimodal payload (text + image parts) when
        # images are present; otherwise we emit the plain string form which all
        # providers accept.
        last = request.messages[-1]
        if last.images:
            chat_messages.append(HumanMessage(content=last.to_dict()))
        else:
            chat_messages.append(_to_langchain_message(last))
        # Create a chat prompt template from the chat messages

        prompt = ChatPromptTemplate.from_messages(chat_messages)

        # Get a chat runnable from the language model service
        # The runnable is determined by the language model ID and temperature from the request

        chat_runnable = llm_service.get_chat_runnable(
            llm_id=request.llm_id, temperature=request.temperature
        )
        # Create a string output parser to parse the output of the chat runnable
        parser = StrOutputParser()

        
        # Create a chain of operations
        # The chat prompt template, chat runnable, and string output parser are chained together
        chain = prompt | chat_runnable | parser
        # Start the chain of operations with an empty input and return the result
        # The result is an asynchronous iterator that yields chat responses

        return chain.astream(input={})
