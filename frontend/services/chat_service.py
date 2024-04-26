from typing import List, Callable, Awaitable

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.chat import ChatMessage, ChatRequest


class ChatService:
    """
    This class represents a chat service that interacts with an AI model to generate chat responses.

    Methods:
        achat: Generates chat responses based on the given parameters.
    """
    @log_decorator
    @staticmethod
    async def achat(
        llm_id: int,
        messages: List[ChatMessage],
        on_changed_fn: Callable[[str], Awaitable[None]],
        on_completed_fn: Callable[[ChatMessage], Awaitable[None]],
        indicator: str = "▌",
        temperature: float = 0,
        persona: str = "neutral",
    ) -> None:
        """
        Generates chat responses based on the given parameters.

        Parameters:
            llm_id (int): The ID of the language model.
            messages (List[ChatMessage]): The list of chat messages.
            on_changed_fn (Callable[[str], Awaitable[None]]): A function to be called when the chat response changes.
            on_completed_fn (Callable[[ChatMessage], Awaitable[None]]): A function to be called when the chat is completed.
            indicator (str, optional): The indicator to show the progress of the chat. Defaults to "▌".
            temperature (float, optional): The temperature parameter for generating responses. Defaults to 0.
            persona (str, optional): The persona of the AI model. Defaults to "neutral".

        Returns:
            None
        """
        message_text = ""
        await on_changed_fn(indicator)

        async for message_text_chunk in HttpUtils.apost_stream(
            url=Config.CHAT_SERVICE_ENDPOINT,
            request=ChatRequest(
                llm_id=llm_id,
                persona=persona,
                messages=messages,
                temperature=temperature,
            ),
        ):
            message_text += message_text_chunk
            await on_changed_fn(message_text + indicator)

        await on_changed_fn(message_text)
        await on_completed_fn(ChatMessage(sender="ai", text=message_text, images=None))
