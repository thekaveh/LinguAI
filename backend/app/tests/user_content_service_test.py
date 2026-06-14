import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.data_access.models.user_content import UserContent as UserContentModel
from app.schema.user_content import UserContentBase, UserContentSearch, UserContent
from app.services.user_content_service import UserContentService

from unittest.mock import create_autospec

@patch('app.services.user_content_service.Config')
@patch('app.services.user_content_service.logging')
@patch('app.services.user_content_service.UserContentModel')
def test_create_user_content(mock_user_content_model, mock_logging, mock_config):
    mock_session = MagicMock(spec=Session)
    service = UserContentService(mock_session)
    user_content_data = UserContentBase(user_id=1, content_type=1, content='Hello, world!', id=1)

    # Create a mock UserContentModel instance with an id attribute
    mock_user_content = create_autospec(UserContentModel, instance=True)
    mock_user_content.id = 1
    mock_user_content.level = "beginner"
    mock_user_content.language = "English"
    mock_user_content.user_content = "Hello, world!"
    mock_user_content.gen_content = "Hello, world!"
    mock_user_content_model.return_value = mock_user_content

    service.create_user_content(user_content_data)
    mock_session.add.assert_called()
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()

@patch('app.services.user_content_service.Config')
@patch('app.services.user_content_service.logging')
def test_read_user_content_v0(mock_logging, mock_config):
    mock_session = MagicMock(spec=Session)
    service = UserContentService(mock_session)
    search_params = UserContentSearch(user_id=1, content_type=1)
    service.read_user_content_v0(search_params)
    mock_session.query.assert_called_with(UserContentModel)

@patch('app.services.user_content_service.Config')
@patch('app.services.user_content_service.logging')
def test_delete_user_content(mock_logging, mock_config):
    mock_session = MagicMock(spec=Session)
    service = UserContentService(mock_session)
    service.delete_user_content(1)
    mock_session.query.assert_called_with(UserContentModel)
    mock_session.delete.assert_called()
    mock_session.commit.assert_called()

@patch('app.services.user_content_service.Config')
@patch('app.services.user_content_service.logging')
def test_read_user_content(mock_logging, mock_config):
    mock_session = MagicMock(spec=Session)
    service = UserContentService(mock_session)
    search_params = UserContentSearch(user_id=1, content_type=1)
    service.read_user_content(search_params)
    mock_session.query.assert_called_with(UserContentModel)