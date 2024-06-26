import pytest
from unittest.mock import AsyncMock, call
from typing import Callable, Awaitable

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.chat import ChatMessage, ChatRequest
from services.chat_service import ChatService


import pytest
from unittest.mock import AsyncMock, call
from typing import Callable, Awaitable
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.chat import ChatMessage, ChatRequest
from services.chat_service import ChatService

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
async def test_achat_success():
    # Define llm_id
    llm_id = 1

    # Mock HttpUtils.apost_stream to return an instance of AsyncIteratorMock
    HttpUtils.apost_stream = AsyncIteratorMock(["chunk1", "chunk2"])

    # Mock the callback functions
    on_changed_fn = AsyncMock()
    on_completed_fn = AsyncMock()

    # Test
    await ChatService.achat(
        llm_id=llm_id,
        messages=[ChatMessage(sender="user", text="Hello")],
        on_changed_fn=on_changed_fn,
        on_completed_fn=on_completed_fn
    )

    # Assertions
    assert HttpUtils.apost_stream.call_args == (
        (),
        {
            "url": Config.CHAT_SERVICE_ENDPOINT,
            "request": ChatRequest(
                llm_id=1,
                persona="neutral",
                messages=[ChatMessage(sender="user", text="Hello")],
                temperature=0,
            ),
        },
    )
    on_changed_fn.assert_awaited_with("chunk1chunk2")
    on_completed_fn.assert_awaited_once()