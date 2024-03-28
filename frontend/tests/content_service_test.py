import pytest
from unittest.mock import AsyncMock, patch
from typing import List

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.content import Content as ContentSchema
from services.content_service import ContentService

@pytest.mark.asyncio
async def test_list_content_success():
    # Mocks
    expected_content = [ContentSchema(content_id=1, content_name="Content 1"), ContentSchema(content_id=2, content_name="Content 2")]
    HttpUtils.get = AsyncMock(return_value=expected_content)

    # Test
    content_list = await ContentService.list()

    # Assertions
    assert content_list == expected_content
    HttpUtils.get.assert_awaited_once_with(Config.CONTENT_SERVICE_LIST_ENDPOINT, response_model=List[ContentSchema])

@pytest.mark.asyncio
async def test_list_content_failure():
    # Mocks
    HttpUtils.get = AsyncMock(side_effect=Exception("Test Exception"))

    # Test and Assertions
    with pytest.raises(Exception, match="Test Exception"):
        await ContentService.list()
