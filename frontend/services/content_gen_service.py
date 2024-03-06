from typing import Callable
from core.config import Config

from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.content_gen import ContentGenReq


class ContentGenService:
    @log_decorator
    @staticmethod
    async def agenerate_content(
        request: ContentGenReq,
        on_next_fn: Callable[[str], None],
        on_completed_fn: Callable[[str], None],
    ) -> None:
        content_text = ""

        async for content_text_chunk in HttpUtils.apost_stream(
            url=Config.CONTENT_GEN_SERVICE_CONTENT_TOPIC_ENDPOINT,
            request=request,
        ):
            content_text += content_text_chunk
            on_next_fn(content_text)

        on_next_fn(content_text)
        on_completed_fn(content_text)
