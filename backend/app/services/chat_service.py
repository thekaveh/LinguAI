from sqlmodel import Session
from typing import AsyncIterable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.messages import HumanMessage, SystemMessage

from app.models.persona import Persona
from app.schema.chat import ChatRequest
from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.services.persona_service import PersonaService
import logging
from app.core.config import Config

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
            ValueError: If the request or any required fields are missing.

        """
        assert request is not None, "message is required"
        assert request.llm_id is not None, "llm_id is required"
        assert request.messages is not None, "messages is required"
        assert len(request.messages) > 0, "messages must not be empty"

        persona_service = PersonaService(self.db_session)
        llm_service = LLMService(self.db_session)

        persona = persona_service.get_by_name(name=request.persona)

        if persona is None:
            raise ValueError("Persona not found")

        chat_messages = [SystemMessage(content=persona.description)] + [
            message.text for message in request.messages[:-1]
        ]
        self.logger.info(f"chat_messages: {chat_messages}")
        self.logger.info(f"request.messages[-1]: {request.messages[-1]}")
        
        # Append the last message from the request to the chat messages list
        # The content of the message is converted to a dictionary

        chat_messages.append(HumanMessage(content=request.messages[-1].to_dict()))
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
