from typing import AsyncIterable
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.rewrite_content_service import RewriteContentService
from app.schema.rewrite_content import ContentRewriteReq
from app.core.config import Config


@pytest.mark.asyncio
@patch.object(RewriteContentService, "_generate_prompt")
@patch("app.services.llm_service.LLMService.get_chat_runnable")
async def test_arewrite_content(mock_get_chat_runnable, mock_generate_prompt):
    mock_db = MagicMock()
    service = RewriteContentService(mock_db)

    mock_request = MagicMock(spec=ContentRewriteReq)
    mock_request.temperature = 0.5
    mock_request.model = "mock_model"
    mock_request.user_base_language = "English"
    mock_request.user_skill_level = "beginner"
    mock_request.language = "English"
    mock_request.input_content = "mock_content"

    mock_generate_prompt.return_value = "mock_prompt"
    mock_get_chat_runnable.return_value = AsyncMock()

    result = await service.arewrite_content(mock_request)

    mock_generate_prompt.assert_called_once_with(mock_request)
    mock_get_chat_runnable.assert_called_once_with(model="mock_model", temperature=0.5)
    assert isinstance(result, AsyncIterable)


@pytest.mark.asyncio
@patch.object(RewriteContentService, "_generate_prompt")
@patch("app.services.llm_service.LLMService.get_chat_runnable")
async def test_arewrite_content_no_temperature(
    mock_get_chat_runnable, mock_generate_prompt
):
    mock_db = MagicMock()
    service = RewriteContentService(mock_db)

    mock_request = MagicMock(spec=ContentRewriteReq)
    mock_request.model = "mock_model"
    mock_request.user_base_language = "English"
    mock_request.user_skill_level = "beginner"
    mock_request.language = "English"
    mock_request.input_content = "mock_content"
    mock_request.temperature = None  # No temperature provided

    mock_generate_prompt.return_value = "mock_prompt"
    mock_get_chat_runnable.return_value = AsyncMock()

    result = await service.arewrite_content(mock_request)

    mock_generate_prompt.assert_called_once_with(mock_request)
    mock_get_chat_runnable.assert_called_once_with(
        model="mock_model", temperature=float(Config.DEFAULT_TEMPERATURE)
    )
    assert isinstance(result, AsyncIterable)


@pytest.mark.asyncio
@patch.object(RewriteContentService, "_generate_prompt")
@patch("app.services.llm_service.LLMService.get_chat_runnable")
async def test_arewrite_content_no_model(mock_get_chat_runnable, mock_generate_prompt):
    mock_db = MagicMock()
    service = RewriteContentService(mock_db)

    mock_request = MagicMock(spec=ContentRewriteReq)
    mock_request.model = None  # No model provided
    mock_request.user_base_language = "English"
    mock_request.user_skill_level = "beginner"
    mock_request.language = "English"
    mock_request.input_content = "mock_content"
    mock_request.temperature = 0.5

    mock_generate_prompt.return_value = "mock_prompt"
    mock_get_chat_runnable.return_value = AsyncMock()

    result = await service.arewrite_content(mock_request)

    mock_generate_prompt.assert_called_once_with(mock_request)
    mock_get_chat_runnable.assert_called_once_with(
        model=Config.DEFAULT_LANGUAGE_TRANSLATION_MODEL, temperature=0.5
    )
    assert isinstance(result, AsyncIterable)


@pytest.mark.asyncio
@patch.object(RewriteContentService, "_generate_prompt")
@patch("app.services.llm_service.LLMService.get_chat_runnable")
async def test_arewrite_content_different_prompt(
    mock_get_chat_runnable, mock_generate_prompt
):
    mock_db = MagicMock()
    service = RewriteContentService(mock_db)

    mock_request = MagicMock(spec=ContentRewriteReq)
    mock_request.model = "mock_model"
    mock_request.user_base_language = "English"
    mock_request.user_skill_level = "beginner"
    mock_request.language = "English"
    mock_request.input_content = "mock_content"
    mock_request.temperature = 0.5

    mock_generate_prompt.return_value = "different_prompt"  # Different prompt
    mock_get_chat_runnable.return_value = AsyncMock()

    result = await service.arewrite_content(mock_request)

    mock_generate_prompt.assert_called_once_with(mock_request)
    mock_get_chat_runnable.assert_called_once_with(model="mock_model", temperature=0.5)
    assert isinstance(result, AsyncIterable)
