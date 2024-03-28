import pytest
from unittest.mock import AsyncMock, call
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.review_writing import ReviewWritingReq
from services.review_writing_service import ReviewWritingService

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

async def test_review_writing_success():
    # Mock HttpUtils.apost_stream to return content chunks
    HttpUtils.apost_stream = AsyncMock(return_value=AsyncIteratorMock(["chunk1", "chunk2"]))
    
    # Mock the callback functions
    on_next_fn = AsyncMock()
    on_completed_fn = AsyncMock()
    
    # Test
    await ReviewWritingService.areview_writing(
        request=ReviewWritingReq(
            user_id=123,
            language="Python",
            curr_skill_level="Intermediate",
            next_skill_level="Advanced",
            strength="Problem solving",
            weakness="Debugging",
            input_content="Some content"
        ),
        on_next_fn=on_next_fn,
        on_completed_fn=on_completed_fn
    )
    
    # Assertions
    HttpUtils.apost_stream.assert_awaited_once_with(
        url=Config.REVIEW_WRITING_SERVICE_ENDPOINT,
        request=ReviewWritingReq(
            user_id=123,
            language="Python",
            curr_skill_level="Intermediate",
            next_skill_level="Advanced",
            strength="Problem solving",
            weakness="Debugging",
            input_content="Some content"
        )
    )
    on_next_fn.assert_has_awaits([
        call("chunk1"),
        call("chunk2")
    ])
    on_completed_fn.assert_awaited_once()
