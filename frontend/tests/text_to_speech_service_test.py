import pytest
from unittest.mock import AsyncMock
from typing import List, Callable

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.text_to_speech import TextToSpeechRequest, TextToSpeechResponse
from services.text_to_speech_service import TextToSpeechService

@pytest.mark.asyncio
async def test_generate_text_to_speech_success():
    # Mock HttpUtils.apost to return a TextToSpeechResponse
    expected_response = TextToSpeechResponse(audio="audio_data")
    HttpUtils.apost = AsyncMock(return_value=expected_response)
    
    # Test
    response = await TextToSpeechService.agenerate("Hello", "en")
    
    # Assertions
    assert response == expected_response
    HttpUtils.apost.assert_awaited_once_with(
        request=TextToSpeechRequest(text="Hello", lang="en"),
        response_model=TextToSpeechResponse,
        url=Config.TEXT_TO_SPEECH_SERVICE_ENDPOINT
    )

@pytest.mark.asyncio
async def test_generate_text_to_speech_exception():
    # Mock HttpUtils.apost to raise an exception
    HttpUtils.apost = AsyncMock(side_effect=Exception("HTTP Error"))
    
    # Test and assertion
    with pytest.raises(Exception, match="HTTP Error"):
        await TextToSpeechService.agenerate("Hello", "en")
    HttpUtils.apost.assert_awaited_once_with(
        request=TextToSpeechRequest(text="Hello", lang="en"),
        response_model=TextToSpeechResponse,
        url=Config.TEXT_TO_SPEECH_SERVICE_ENDPOINT
    )
