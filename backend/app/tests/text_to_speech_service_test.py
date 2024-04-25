import base64
import pytest
from unittest.mock import Mock, patch
from app.schema.text_to_speech import TextToSpeechRequest, TextToSpeechResponse
from app.services.text_to_speech_service import TextToSpeechService

@patch('app.services.text_to_speech_service.gTTS')
@patch('app.services.text_to_speech_service.BytesIO')
def test_generate(mock_bytes_io, mock_gtts):
    # Arrange
    request = TextToSpeechRequest(text="Hello, world!", lang="en")
    service = TextToSpeechService()

    mock_audio_buffer = Mock()
    mock_bytes_io.return_value.__enter__.return_value = mock_audio_buffer

    mock_audio_buffer.getvalue.return_value = b"audio data"
    expected_audio_base64 = base64.b64encode(b"audio data").decode("utf-8")
    expected_audio_data = f"data:audio/mpeg;base64,{expected_audio_base64}"

    # Act
    response = service.generate(request)

    # Assert
    mock_gtts.assert_called_once_with(text=request.text, lang=request.lang)
    mock_audio_buffer.seek.assert_called_once_with(0)
    mock_audio_buffer.getvalue.assert_called_once()

    assert response.audio == expected_audio_data
    assert response.lang == request.lang