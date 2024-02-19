from typing import List, Tuple, Callable

from core.config import Config
from models.chat_req import ChatReq
from utils.http_utils import HttpUtils

class ChatService:
    @staticmethod
    async def achat(
        model				: str
        , messages			: List[Tuple[str, str]]
        , on_next_msg_chunk	: Callable[[str], None]
        , indicator			: str 					= "▌"
        , temperature		: float 				= 0
        , persona			: str 					= "neutral"
    ) -> List[Tuple[str, str]]:
        full_msg = ""
        on_next_msg_chunk(indicator)

        async for msg_chunk in HttpUtils.apost_stream(
            url=Config.CHAT_SERVICE_ENDPOINT
            , request=ChatReq(
				model=model
				, persona=persona
				, messages=messages
				, temperature=temperature
			)
        ):
            full_msg += msg_chunk
            on_next_msg_chunk(full_msg + indicator)

        on_next_msg_chunk(full_msg)
        messages.append(("ai", full_msg))
        
        return messages
