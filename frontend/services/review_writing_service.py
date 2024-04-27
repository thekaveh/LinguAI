from core.config import Config
from typing import Callable, Awaitable

from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.review_writing import ReviewWritingReq


class ReviewWritingService:
    """
    This class provides methods for writing reviews.

    Methods:
    - areview_writing: Writes a review asynchronously.
    """

    @log_decorator
    @staticmethod
    async def areview_writing(
        request: ReviewWritingReq,
        on_changed_fn: Callable[[str], Awaitable[None]],
        on_completed_fn: Callable[[str], Awaitable[None]],
        indicator: str = "▌",
    ) -> None:
        """
        Writes a review asynchronously.

        Args:
        - request: The review writing request.
        - on_changed_fn: A callback function to be called when the content changes.
        - on_completed_fn: A callback function to be called when the writing is completed.
        - indicator: The indicator to show progress.

        Returns:
        None
        """
        content_txt = ""
        on_changed_fn(indicator)

        async for content_text_chunk in HttpUtils.apost_stream(
            url=Config.REVIEW_WRITING_SERVICE_ENDPOINT,
            request=request,
        ):
            content_txt += content_text_chunk
            await on_changed_fn(content_txt + indicator)

        await on_changed_fn(content_txt)
        await on_completed_fn(content_txt)
