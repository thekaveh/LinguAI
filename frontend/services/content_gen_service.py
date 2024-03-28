from core.config import Config
from typing import Callable, Awaitable

from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.content_gen import ContentGenReq


class ContentGenService:
    @log_decorator
    @staticmethod
    async def agenerate_content(
        request: ContentGenReq,
        on_changed_fn: Callable[[str], Awaitable[None]],
        on_completed_fn: Callable[[str], Awaitable[None]],
        indicator: str = "▌",
    ) -> None:
        content_txt = ""
        on_changed_fn(indicator)

        async for content_text_chunk in HttpUtils.apost_stream(
            url=Config.CONTENT_GEN_SERVICE_CONTENT_TOPIC_ENDPOINT,
            request=request,
        ):
            content_txt += content_text_chunk
            await on_changed_fn(content_txt + indicator)

        await on_changed_fn(content_txt)
        await on_completed_fn(content_txt)
