from typing import AsyncIterable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.messages import HumanMessage, SystemMessage

from app.services.llm_service import LLMService
from app.services.persona_service import PersonaService
from app.models.messages.chat_message import ChatMessage


class ChatService:
    @staticmethod
    async def achat(message: ChatMessage) -> AsyncIterable[str]:
        assert message is not None, "message is required"
        assert message.model is not None, "model is required"
        assert message.messages is not None, "messages is required"
        assert len(message.messages) > 0, "messages must not be empty"

        chat_messages = [
            SystemMessage(
                content=PersonaService.get_persona(message.persona).description
            )
        ] + message.messages[:-1]

        latest_message_content = [{"type": "text", "text": message.messages[-1][1]}]
        if message.images and len(message.images) > 0:
            latest_message_content += [
                {"type": "image_url", "image_url": f"data:image/png;base64,{image}"}
                for image in message.images
            ]
        chat_messages.append(HumanMessage(content=latest_message_content))

        prompt = ChatPromptTemplate.from_messages(chat_messages)
        chat_runnable = LLMService.get_chat_runnable(
            model=message.model, temperature=message.temperature
        )
        parser = StrOutputParser()

        chain = prompt | chat_runnable | parser

        return chain.astream(input={})
