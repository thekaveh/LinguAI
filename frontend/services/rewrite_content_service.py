from core.config import Config
from typing import Callable, Awaitable

from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.rewrite_content import ContentRewriteReq


class RewriteContentService:
    """
    This class provides a service for rewriting content.

    Args:
        request (ContentRewriteReq): The request object for content rewriting.
        on_changed_fn (Callable[[str], Awaitable[None]]): A callback function called when the content changes.
        on_completed_fn (Callable[[str], Awaitable[None]]): A callback function called when the content rewriting is completed.
        indicator (str, optional): An indicator to show the progress of content rewriting. Defaults to "▌".

    """

    @log_decorator
    @staticmethod
    async def arewrite_content(
        request: ContentRewriteReq,
        on_changed_fn: Callable[[str], Awaitable[None]],
        on_completed_fn: Callable[[str], Awaitable[None]],
        indicator: str = "▌",
    ) -> None:
        """
        Rewrite the content asynchronously.

        Args:
            request (ContentRewriteReq): The request object for content rewriting.
            on_changed_fn (Callable[[str], Awaitable[None]]): A callback function called when the content changes.
            on_completed_fn (Callable[[str], Awaitable[None]]): A callback function called when the content rewriting is completed.
            indicator (str, optional): An indicator to show the progress of content rewriting. Defaults to "▌".

        Returns:
            None

        """
        content_txt = ""
        on_changed_fn(indicator)

        async for content_text_chunk in HttpUtils.apost_stream(
            url=Config.REWRITE_CONTENT_SERVICE_ENDPOINT,
            request=request,
        ):
            content_txt += content_text_chunk
            await on_changed_fn(content_txt + indicator)

        await on_changed_fn(content_txt)
        await on_completed_fn(content_txt)
