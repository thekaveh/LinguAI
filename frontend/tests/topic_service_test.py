import pytest
from unittest.mock import AsyncMock
from typing import List
from services.topic_service import TopicService
from core.config import Config
from utils.http_utils import HttpUtils
from schema.topic import Topic as TopicSchema

@pytest.mark.asyncio
async def test_list_topics_success():
    # Mocks
    expected_topics = [TopicSchema(topic_id=1, topic_name="sports"), TopicSchema(topic_id=2, topic_name="nutrition")]
    HttpUtils.get = AsyncMock(return_value=expected_topics)

    # Test
    topics = await TopicService.list()

    # Assertions
    assert all(topic in topics for topic in expected_topics)
    HttpUtils.get.assert_awaited_once_with(Config.TOPIC_SERVICE_LIST_ENDPOINT, response_model=List[TopicSchema])

@pytest.mark.asyncio
async def test_list_topics_failure():
    # Mocks
    HttpUtils.get = AsyncMock(side_effect=Exception("Test Exception"))

    # Test and Assertions
    with pytest.raises(Exception, match="Test Exception"):
        await TopicService.list()
