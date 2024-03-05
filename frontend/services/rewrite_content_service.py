from typing import Callable
from core.config import Config

from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.rewrite_content import ContentRewriteReq


class RewriteContentService:
    @log_decorator
    @staticmethod
    async def rewrite_content(
        request: ContentRewriteReq,
        on_next_fn: Callable[[str], None],
        on_completed_fn: Callable[[], None],
    ) -> None:
        async for content_text_chunk in HttpUtils.apost_stream(
            url=Config.REWRITE_CONTENT_SERVICE_ENDPOINT,
            request=request,
        ):
            # Call on_next_fn with just the new chunk, without appending the indicator
            on_next_fn(content_text_chunk)

        on_completed_fn()
