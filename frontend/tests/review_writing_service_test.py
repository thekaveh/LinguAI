import pytest
from unittest.mock import AsyncMock, call
from typing import Callable, Awaitable
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.review_writing import ReviewWritingReq
from services.review_writing_service import ReviewWritingService

class AsyncIteratorMock:
    def __init__(self, chunks):
        self.chunks = chunks
        self.call_args = None

    def __call__(self, *args, **kwargs):
        self.call_args = (args, kwargs)

        class _AsyncIterator:
            def __init__(self, chunks):
                self.chunks = chunks
                self.index = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.index < len(self.chunks):
                    result = self.chunks[self.index]
                    self.index += 1
                    return result
                else:
                    raise StopAsyncIteration

        return _AsyncIterator(self.chunks)

@pytest.mark.asyncio
async def test_areview_writing_success():
    # Mock HttpUtils.apost_stream to return an instance of AsyncIteratorMock
    HttpUtils.apost_stream = AsyncIteratorMock(["chunk1", "chunk2"])

    # Mock the callback functions
    on_changed_fn = AsyncMock()
    on_completed_fn = AsyncMock()

    # Test
    await ReviewWritingService.areview_writing(
        request=ReviewWritingReq(
            llm_id=1,
            user_id=1,
            language="English",
            curr_skill_level="beginner",
            next_skill_level="intermediate",
            strength="creativity",
            weakness="grammar",
            input_content="This is a test content.",
            model="gpt-3",
            temperature=0.5
        ),
        on_changed_fn=on_changed_fn,
        on_completed_fn=on_completed_fn
    )

    # Assertions
    assert HttpUtils.apost_stream.call_args == (
        (),
        {
            "url": Config.REVIEW_WRITING_SERVICE_ENDPOINT,
            "request": ReviewWritingReq(
                llm_id=1,
                user_id=1,
                language="English",
                curr_skill_level="beginner",
                next_skill_level="intermediate",
                strength="creativity",
                weakness="grammar",
                input_content="This is a test content.",
                model="gpt-3",
                temperature=0.5
            ),
        },
    )
    on_changed_fn.assert_has_calls([
        call("▌"),
        call("chunk1▌"),
        call("chunk1chunk2▌"),
        call("chunk1chunk2")
    ])
    on_completed_fn.assert_awaited_once_with("chunk1chunk2")