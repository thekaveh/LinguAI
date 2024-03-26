import pytest
from unittest.mock import AsyncMock
from typing import List
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.language import Language as LanguageSchema
from services.language_service import LanguageService

@pytest.mark.asyncio
async def test_list_languages_success():
    # Mock HttpUtils.get to return a list of languages
    expected_languages = [
        LanguageSchema(language_name="English", language_id="1"),
        LanguageSchema(language_name="French", language_id="5"),
    ]
    HttpUtils.get = AsyncMock(return_value=expected_languages)
    
    # Test
    languages = await LanguageService.list()
    
    # Assertions
    assert languages == expected_languages
    HttpUtils.get.assert_awaited_once_with(Config.LANGUAGE_SERVICE_LIST_ENDPOINT, response_model=List[LanguageSchema])

@pytest.mark.asyncio
async def test_list_languages_exception():
    # Mock HttpUtils.get to raise an exception
    HttpUtils.get = AsyncMock(side_effect=Exception("HTTP Error"))
    
    # Test and assertion
    with pytest.raises(Exception, match="HTTP Error"):
        await LanguageService.list()
    HttpUtils.get.assert_awaited_once_with(Config.LANGUAGE_SERVICE_LIST_ENDPOINT, response_model=List[LanguageSchema])
