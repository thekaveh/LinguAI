from typing import List, Tuple, Callable

from core.config import Config
from utils.http_utils import HttpUtils
from models.messages.chat_message import ChatMessage


class ChatService:
    @staticmethod
    async def achat(
        model: str,
        messages: List[Tuple[str, str]],
        on_next_chunk: Callable[[str], None],
        indicator: str = "▌",
        temperature: float = 0,
        persona: str = "neutral",
    ) -> List[Tuple[str, str]]:
        full_msg = ""
        on_next_chunk(indicator)

        async for msg_chunk in HttpUtils.apost_stream(
            url=Config.CHAT_SERVICE_ENDPOINT,
            request=ChatMessage(
                model=model,
                persona=persona,
                temperature=temperature,
                messages=messages,
            ),
        ):
            full_msg += msg_chunk
            on_next_chunk(full_msg + indicator)

        on_next_chunk(full_msg)
        messages.append(("ai", full_msg))

        return messages
