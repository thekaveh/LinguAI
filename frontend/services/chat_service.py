from typing import List, Callable

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from models.common.chat_message import ChatMessage
from models.common.chat_request import ChatRequest


class ChatService:
    @log_decorator
    @staticmethod
    async def achat(
        model: str,
        messages: List[ChatMessage],
        on_next_fn: Callable[[str], None],
        on_completed_fn: Callable[[ChatMessage], None],
        indicator: str = "▌",
        temperature: float = 0,
        persona: str = "neutral",
    ) -> None:
        message_text = ""
        on_next_fn(indicator)

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
            on_next_fn(message_text + indicator)

        on_next_fn(message_text)
        on_completed_fn(ChatMessage(sender="ai", text=message_text, images=None))
