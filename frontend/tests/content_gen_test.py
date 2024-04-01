import pytest
from unittest.mock import AsyncMock, call
from typing import Callable, Awaitable
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.content_gen import ContentGenReq, Content, Language
from services.content_gen_service import ContentGenService

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
async def test_agenerate_content_success():
    # Mock HttpUtils.apost_stream to return an instance of AsyncIteratorMock
    HttpUtils.apost_stream = AsyncIteratorMock(["chunk1", "chunk2"])

    # Mock the callback functions
    on_changed_fn = AsyncMock()
    on_completed_fn = AsyncMock()

    # Test
    await ContentGenService.agenerate_content(
        request=ContentGenReq(
            user_id=1,
            user_topics=["topic1", "topic2"],
            content=Content(content_id=1, content_name="story"),
            language=Language(language_id=1, language_name="English"),
            skill_level="beginner",
            model_name="gpt-3",
            temperature=0.5
        ),
        on_changed_fn=on_changed_fn,
        on_completed_fn=on_completed_fn
    )

    # Assertions
    assert HttpUtils.apost_stream.call_args == (
        (),
        {
            "url": Config.CONTENT_GEN_SERVICE_CONTENT_TOPIC_ENDPOINT,
            "request": ContentGenReq(
                user_id=1,
                user_topics=["topic1", "topic2"],
                content=Content(content_id=1, content_name="story"),
                language=Language(language_id=1, language_name="English"),
                skill_level="beginner",
                model_name="gpt-3",
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