import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from sqlalchemy.orm import Session
from app.schema.review_writing import ReviewWritingReq
from app.services.review_writing_service import ReviewWritingService

class TestReviewWritingService:
    def setup_method(self):
        self.mock_session = MagicMock(spec=Session)
        self.service = ReviewWritingService(self.mock_session)

    @pytest.mark.asyncio
    @patch.object(ReviewWritingService, '_generate_prompt')
    @patch('app.services.llm_service.LLMService.get_chat_runnable')
    async def test_areview_writing(self, mock_get_chat_runnable, mock_generate_prompt):
        mock_request = MagicMock(spec=ReviewWritingReq)
        mock_request.model = 'mock_model'
        mock_request.temperature = 0.5
        mock_generate_prompt.return_value = 'mock_prompt'
        mock_get_chat_runnable.return_value = AsyncMock()
        result = await self.service.areview_writing(mock_request)
        mock_generate_prompt.assert_called_once_with(mock_request)
        mock_get_chat_runnable.assert_called_once()

    def test_generate_prompt(self):
        mock_request = MagicMock(spec=ReviewWritingReq)
        mock_request.curr_skill_level = 'beginner'
        mock_request.language = 'English'
        mock_request.next_skill_level = 'intermediate'
        mock_request.strength = 'grammar'
        mock_request.weakness = 'vocabulary'
        mock_request.input_content = 'This is a test.'
        result = self.service._generate_prompt(mock_request)
        assert 'The writer of the following text is currently at beginner skill level in English language.' in result