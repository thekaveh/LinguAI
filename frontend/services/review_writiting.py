from typing import Callable
from core.config import Config

from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.review_writing import ReviewWritingReq


class ReviewWritingService:
    @log_decorator
    @staticmethod
    async def areview_writing(
        request: ReviewWritingReq,
        on_next_fn: Callable[[str], None],
        on_completed_fn: Callable[[], None],
    ) -> None:
        async for content_text_chunk in HttpUtils.apost_stream(
            url=Config.REVIEW_WRITING_SERVICE_ENDPOINT,
            request=request,
        ):
            # Call on_next_fn with just the new chunk, without appending the indicator
            on_next_fn(content_text_chunk)

        on_completed_fn()
