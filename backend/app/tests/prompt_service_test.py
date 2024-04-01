import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.data_access.models.prompt import Prompt
from app.schema.prompt import PromptCreate, PromptUpdate, PromptSearch
from app.data_access.repositories.prompt_repository import PromptRepository
from app.services.prompt_service import PromptService

class TestPromptService(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=Session)
        self.mock_repository = MagicMock(spec=PromptRepository)
        self.service = PromptService(self.mock_session)
        self.service.prompt_repository = self.mock_repository

    def test_create_prompt(self):
        mock_prompt_create = MagicMock(spec=PromptCreate)
        self.service.create_prompt(mock_prompt_create)
        self.mock_repository.create.assert_called_once_with(mock_prompt_create)

    def test_update_prompt(self):
        mock_prompt_update = MagicMock(spec=PromptUpdate)
        mock_prompt = MagicMock(spec=Prompt)
        self.mock_repository.find_by_prompt_id.return_value = mock_prompt
        self.service.update_prompt(1, mock_prompt_update)
        self.mock_repository.find_by_prompt_id.assert_called_once_with(1)
        self.mock_repository.update.assert_called_once_with(mock_prompt, mock_prompt_update)

    def test_delete_prompt(self):
        self.service.delete_prompt(1)
        self.mock_repository.delete.assert_called_once_with(1)

    def test_get_prompt_by_id(self):
        self.service.get_prompt_by_id(1)
        self.mock_repository.find_by_prompt_id.assert_called_once_with(1)

    def test_get_all_prompts(self):
        self.service.get_all_prompts()
        self.mock_repository.find_all.assert_called_once()

    def test_get_prompt_by_search_criteria(self):
        mock_search_criteria = MagicMock(spec=PromptSearch)
        self.service.get_prompt_by_search_criteria(mock_search_criteria)
        self.mock_repository.find_by_search_criteria.assert_called_once_with(mock_search_criteria)

if __name__ == '__main__':
    unittest.main()