import pytest
from typing import List
from unittest.mock import patch, AsyncMock
from schema.user_content import UserContentBase, UserContentSearch, UserContent
from services.user_content_service import UserContentService
import datetime

@patch('services.user_content_service.HttpUtils.apost', new_callable=AsyncMock)
@patch('services.user_content_service.Config')
@pytest.mark.asyncio
async def test_create_user_content(mock_config, mock_apost):
    # Arrange
    mock_config.USER_CONTENT_SERVICE_ENDPOINT = 'http://test-endpoint.com'
    user_content = UserContentBase(
        user_id=1,
        level="beginner",
        language="English",
        user_content="Test content",
        gen_content="Generated content",
        type=1,
        created_date=datetime.datetime.now(),
        expiry_date=datetime.datetime.now() + datetime.timedelta(days=1)
    )
    expected_user_content = UserContent(**user_content.dict(), id=1)
    mock_apost.return_value = expected_user_content

    # Act
    result = await UserContentService.create_user_content(user_content)

    # Assert
    mock_apost.assert_awaited_once_with(
        mock_config.USER_CONTENT_SERVICE_ENDPOINT,
        user_content,
        response_model=UserContent
    )
    assert result == expected_user_content

@patch('services.user_content_service.HttpUtils.apost', new_callable=AsyncMock)
@patch('services.user_content_service.Config')
@pytest.mark.asyncio
async def test_search_user_contents(mock_config, mock_apost):
    # Arrange
    mock_config.USER_CONTENT_SERVICE_SEARCH_ENDPOINT = 'http://test-endpoint.com'
    search_params = UserContentSearch(user_id=1, content_type=1)
    expected_user_contents = [UserContent(id=1, content="Test content", user_id=1)]
    mock_apost.return_value = expected_user_contents

    # Act
    result = await UserContentService.search_user_contents(search_params)

    # Assert
    mock_apost.assert_awaited_once_with(
        mock_config.USER_CONTENT_SERVICE_SEARCH_ENDPOINT,
        search_params,
        response_model=List[UserContent]
    )
    assert result == expected_user_contents

@patch('services.user_content_service.HttpUtils.delete', new_callable=AsyncMock)
@patch('services.user_content_service.Config')
@pytest.mark.asyncio
async def test_delete_user_content(mock_config, mock_delete):
    # Arrange
    mock_config.USER_CONTENT_SERVICE_ENDPOINT = 'http://test-endpoint.com'
    content_id = 1

    # Act
    result = await UserContentService.delete_user_content(content_id)

    # Assert
    mock_delete.assert_awaited_once_with(
        f"{mock_config.USER_CONTENT_SERVICE_ENDPOINT}{content_id}"
    )
    assert result == {"message": "Content deleted successfully"}