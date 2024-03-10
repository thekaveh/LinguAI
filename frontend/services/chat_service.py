from typing import List, Callable, Awaitable

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.chat import ChatMessage, ChatRequest


class ChatService:
    @log_decorator
    @staticmethod
    async def achat(
        model: str,
        messages: List[ChatMessage],
        on_changed_fn: Callable[[str], Awaitable[None]],
        on_completed_fn: Callable[[ChatMessage], Awaitable[None]],
        indicator: str = "▌",
        temperature: float = 0,
        persona: str = "neutral",
    ) -> None:
        message_text = ""
        await on_changed_fn(indicator)

        async for message_text_chunk in HttpUtils.apost_stream(
            url=Config.CHAT_SERVICE_ENDPOINT,
            request=ChatRequest(
                model=model,
                persona=persona,
                messages=messages,
                temperature=temperature,
            ),
        ):
            message_text += message_text_chunk
            await on_changed_fn(message_text + indicator)

        await on_changed_fn(message_text)
        await on_completed_fn(ChatMessage(sender="ai", text=message_text, images=None))
