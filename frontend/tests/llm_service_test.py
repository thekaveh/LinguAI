import pytest
from unittest.mock import patch, AsyncMock
from services.llm_service import LLMService
from models.llm import LLM
from core.config import Config
from typing import List

class TestLLMService:
    @pytest.mark.asyncio
    @patch('services.llm_service.HttpUtils.get', new_callable=AsyncMock)
    async def test_aget_all(self, mock_get):
        # Arrange
        mock_llm = LLM(id=1, is_active=True, vision=1, content=1, embeddings=1, provider="provider", name="name")
        mock_get.return_value = [mock_llm, mock_llm]

        # Act
        result = await LLMService.aget_all()

        # Assert
        mock_get.assert_called_once_with(Config.LLM_SERVICE_GET_ALL_ENDPOINT, response_model=List[LLM])
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].is_active == True

    @pytest.mark.asyncio
    @patch('services.llm_service.HttpUtils.get', new_callable=AsyncMock)
    async def test_aget_content(self, mock_get):
        # Arrange
        mock_llm = LLM(id=1, is_active=True, vision=1, content=1, embeddings=1, provider="provider", name="name")
        mock_get.return_value = [mock_llm, mock_llm]

        # Act
        result = await LLMService.aget_content()

        # Assert
        mock_get.assert_called_once_with(Config.LLM_SERVICE_GET_CONTENT_ENDPOINT, response_model=List[LLM])
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].is_active == True

    @pytest.mark.asyncio
    @patch('services.llm_service.HttpUtils.get', new_callable=AsyncMock)
    async def test_aget_vision(self, mock_get):
        # Arrange
        mock_llm = LLM(id=1, is_active=True, vision=1, content=1, embeddings=1, provider="provider", name="name")
        mock_get.return_value = [mock_llm, mock_llm]

        # Act
        result = await LLMService.aget_vision()

        # Assert
        mock_get.assert_called_once_with(Config.LLM_SERVICE_GET_VISION_ENDPOINT, response_model=List[LLM])
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].is_active == True

    @pytest.mark.asyncio
    @patch('services.llm_service.HttpUtils.get', new_callable=AsyncMock)
    async def test_aget_embeddings(self, mock_get):
        # Arrange
        mock_llm = LLM(id=1, is_active=True, vision=1, content=1, embeddings=1, provider="provider", name="name")
        mock_get.return_value = [mock_llm, mock_llm]

        # Act
        result = await LLMService.aget_embeddings()

        # Assert
        mock_get.assert_called_once_with(Config.LLM_SERVICE_GET_EMBEDDINGS_ENDPOINT, response_model=List[LLM])
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].is_active == True