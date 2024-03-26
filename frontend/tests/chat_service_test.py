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

# @pytest.mark.asyncio
async def test_achat_success():
    # Mock HttpUtils.apost_stream to return an instance of AsyncIteratorMock
    HttpUtils.apost_stream = AsyncMock(return_value=AsyncIteratorMock(["chunk1", "chunk2"]))

    # Mock the callback functions
    on_changed_fn = AsyncMock()
    on_completed_fn = AsyncMock()

    # Test
    await ChatService.achat(
        model="test_model",
        messages=[ChatMessage(sender="user", text="Hello")],
        on_changed_fn=on_changed_fn,
        on_completed_fn=on_completed_fn
    )

    # Assertions
    HttpUtils.apost_stream.assert_awaited_once_with(
        url=Config.CHAT_SERVICE_ENDPOINT,
        request=ChatRequest(
            model="test_model",
            persona="neutral",
            messages=[ChatMessage(sender="user", text="Hello")],
            temperature=0,
        )
    )
    on_changed_fn.assert_awaited_with("▌chunk1▌chunk2▌")
    on_completed_fn.assert_awaited_once()
