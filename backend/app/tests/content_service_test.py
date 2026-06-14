import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.schema.content import ContentCreate, Content as ContentSchema
from app.data_access.models.content import Content
from app.services.content_service import ContentService

class TestContentService:
    @pytest.fixture
    def setup(self):
        session = Mock(spec=Session)
        return session

    @patch('app.data_access.repositories.content_repository.ContentRepository.create')
    def test_create_content(self, mock_create, setup):
        # Arrange
        content_service = ContentService(db=setup)
        content_create = ContentCreate(content_name="Test Content")

        mock_content = Mock(spec=Content)
        mock_content.content_name = "Test Content"
        mock_content.content_id = 1  # Add this line
        mock_create.return_value = mock_content

    @patch('app.data_access.repositories.content_repository.ContentRepository.find_by_content_id')
    def test_get_content_by_id(self, mock_find_by_content_id, setup):
        # Arrange
        content_service = ContentService(db=setup)

        mock_content = Mock(spec=Content)
        mock_content.content_name = "Test Content"
        mock_content.content_id = 1  # Add this line
        mock_find_by_content_id.return_value = mock_content

    @patch('app.data_access.repositories.content_repository.ContentRepository.find_all')       
    def test_get_all_content(self, mock_find_all, setup):
        # Arrange
        content_service = ContentService(db=setup)

        mock_content = Mock(spec=Content)
        mock_content.content_name = "Test Content"
        mock_content.content_id = 1  # Add this line
        mock_find_all.return_value = [mock_content]

    @patch('app.data_access.repositories.content_repository.ContentRepository.find_by_content_id')
    @patch('app.data_access.repositories.content_repository.ContentRepository.update')
    def test_update_content(self, mock_update, mock_find_by_content_id, setup):
        # Arrange
        content_service = ContentService(db=setup)
        content_update = ContentCreate(content_name="Updated Content")

        mock_content = Mock(spec=Content)
        mock_content.content_name = "Updated Content"
        mock_content.content_id = 1  # Add this line
        mock_find_by_content_id.return_value = mock_content