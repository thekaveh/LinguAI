import pytest
from unittest.mock import AsyncMock, call
from typing import Callable
from core.config import Config

from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.rewrite_content import ContentRewriteReq
from services.rewrite_content_service import RewriteContentService

class AsyncIteratorMock:
    def __init__(self, chunks):
        self.chunks = chunks
        self.index = 0

    async def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index < len(self.chunks):
            chunk = self.chunks[self.index]
            self.index += 1
            return chunk
        else:
            raise StopAsyncIteration

# Modify the test to use the AsyncIteratorMock
async def test_rewrite_content_success():
    # Mock HttpUtils.apost_stream to return content chunks
    HttpUtils.apost_stream = AsyncMock(return_value=AsyncIteratorMock(["chunk1", "chunk2"]))
    
    # Mock the callback functions
    on_next_fn = AsyncMock()
    on_completed_fn = AsyncMock()
    
    # Test
    await RewriteContentService.arewrite_content(
        request=ContentRewriteReq(user_id=1, language="english", skill_level="advanced", input_content="Some content"),  # Pass the required arguments
        on_next_fn=on_next_fn,
        on_completed_fn=on_completed_fn
    )
    
    # Assertions
    HttpUtils.apost_stream.assert_awaited_once_with(
        url=Config.REWRITE_CONTENT_SERVICE_ENDPOINT,
        request=ContentRewriteReq(user_id=1, language="english", skill_level="advanced", input_content="Some content")  # Pass the required arguments
    )
    on_next_fn.assert_has_awaits([
        call("chunk1"),
        call("chunk2")
    ])
    on_completed_fn.assert_awaited_once()
