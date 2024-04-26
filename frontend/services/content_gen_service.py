from core.config import Config
from typing import Callable, Awaitable
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.content_gen import ContentGenReq

class ContentGenService:
    """
    Service class for asynchronously generating content by making HTTP requests to a content generation service.
    """
    @log_decorator
    @staticmethod
    async def agenerate_content(
        request: ContentGenReq,
        on_changed_fn: Callable[[str], Awaitable[None]],
        on_completed_fn: Callable[[str], Awaitable[None]],
        indicator: str = "▌",
    ) -> None:
        """
        Asynchronously generates content by making HTTP requests to a content generation service.

        Args:
            request (ContentGenReq): The request object containing the necessary parameters for content generation.
            on_changed_fn (Callable[[str], Awaitable[None]]): A callback function to be called when the content changes.
            on_completed_fn (Callable[[str], Awaitable[None]]): A callback function to be called when content generation is completed.
            indicator (str, optional): The indicator character to show progress. Defaults to "▌".

        Returns:
            None
        """
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
