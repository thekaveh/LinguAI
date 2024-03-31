import pytest
from unittest.mock import AsyncMock, call
from typing import Callable, Awaitable
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.rewrite_content import ContentRewriteReq
from services.rewrite_content_service import RewriteContentService

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
async def test_arewrite_content_success():
    # Mock HttpUtils.apost_stream to return an instance of AsyncIteratorMock
    HttpUtils.apost_stream = AsyncIteratorMock(["chunk1", "chunk2"])

    # Mock the callback functions
    on_changed_fn = AsyncMock()
    on_completed_fn = AsyncMock()

    # Test
    await RewriteContentService.arewrite_content(
        request=ContentRewriteReq(
            user_id=1,
            language="English",
            skill_level="beginner",
            input_content="This is a test content.",
            model="gpt-3",
            temperature=0.5,
            user_skill_level="intermediate",
            user_base_language="English"
        ),
        on_changed_fn=on_changed_fn,
        on_completed_fn=on_completed_fn
    )

    # Assertions
    assert HttpUtils.apost_stream.call_args == (
        (),
        {
            "url": Config.REWRITE_CONTENT_SERVICE_ENDPOINT,
            "request": ContentRewriteReq(
                user_id=1,
                language="English",
                skill_level="beginner",
                input_content="This is a test content.",
                model="gpt-3",
                temperature=0.5,
                user_skill_level="intermediate",
                user_base_language="English"
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