from typing import AsyncIterable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.messages import HumanMessage, SystemMessage

from app.services.llm_service import LLMService
from app.models.common.chat_request import ChatRequest
from app.services.persona_service import PersonaService


class ChatService:
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

        # latest_message_content = [{"type": "text", "text": request.messages[-1][1]}]
        # if request.images and (
        #     not request.model.startswith("gpt-")
        #     or request.model == "gpt-4-vision-preview"
        # ):
        #     latest_message_content += [
        #         {"type": "image_url", "image_url": image} for image in request.images
        #     ]

        chat_messages.append(HumanMessage(content=request.messages[-1].to_dict()))

        prompt = ChatPromptTemplate.from_messages(chat_messages)
        print(prompt)
        chat_runnable = LLMService.get_chat_runnable(
            model=request.model, temperature=request.temperature
        )
        parser = StrOutputParser()

        chain = prompt | chat_runnable | parser

        return chain.astream(input={})
