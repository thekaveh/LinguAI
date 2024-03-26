import pytest
from unittest.mock import AsyncMock, call
from typing import Callable
from core.config import Config
from schema.content import Content
from schema.language import Language
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.content_gen import ContentGenReq
from services.content_gen_service import ContentGenService

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

async def test_agenerate_content_success():
    # Mock HttpUtils.apost_stream to return an instance of AsyncIteratorMock
    HttpUtils.apost_stream = AsyncMock(return_value=AsyncIteratorMock(["chunk1", "chunk2"]))

    # Mock the callback functions
    on_next_fn = AsyncMock()
    on_completed_fn = AsyncMock()

    # Test
    await ContentGenService.agenerate_content(
        request=ContentGenReq(user_id=1, user_topics=["topic1", "topic2"], content=Content(content_id=1, content_name="story"), language=Language(language_id=1, language_name="English")),
        on_next_fn=on_next_fn,
        on_completed_fn=on_completed_fn
    )

    # Assertions
    HttpUtils.apost_stream.assert_awaited_once_with(
        url=Config.CONTENT_GEN_SERVICE_CONTENT_TOPIC_ENDPOINT,
        request=ContentGenReq(user_id=1, user_topics=["topic1", "topic2"], content=Content(content_id=1, content_name="story"), language=Language(language_id=1, language_name="English"))
    )
    on_next_fn.assert_has_awaits([
        call("chunk1"),
        call("chunk1chunk2")
    ])
    on_completed_fn.assert_awaited_once_with("chunk1chunk2")
