import pytest
from unittest.mock import AsyncMock
from typing import List
from core.config import Config
from schema.list_response import ListResponse
from services.llm_service import LLMService
from utils.http_utils import HttpUtils

@pytest.mark.asyncio
async def test_list_models_success():
    # Mock HttpUtils.get to return a ListResponse object with results
    HttpUtils.get = AsyncMock(return_value=ListResponse(result=["model1", "model2"]))

    # Test and assertion
    result = await LLMService.list_models()
    assert result == ["model1", "model2"]
    HttpUtils.get.assert_awaited_once_with(Config.LLM_SERVICE_LIST_MODELS_ENDPOINT, response_model=ListResponse)

@pytest.mark.asyncio
async def test_list_vision_models_success():
    # Mock HttpUtils.get to return a ListResponse object with results
    HttpUtils.get = AsyncMock(return_value=ListResponse(result=["vision_model1", "vision_model2"]))

    # Test and assertion
    result = await LLMService.list_vision_models()
    assert result == ["vision_model1", "vision_model2"]
    HttpUtils.get.assert_awaited_once_with(Config.LLM_SERVICE_LIST_VISION_MODELS_ENDPOINT, response_model=ListResponse)
