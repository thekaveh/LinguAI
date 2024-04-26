from typing import List, Callable

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.text_to_speech import TextToSpeechRequest, TextToSpeechResponse


class TextToSpeechService:
    """
    Service class for converting text to speech.
    """

    @log_decorator
    @staticmethod
    async def agenerate(text: str, lang: str) -> TextToSpeechResponse:
        """
        Asynchronously generates speech from the given text in the specified language.

        Args:
            text (str): The text to convert to speech.
            lang (str): The language code for the desired speech output.

        Returns:
            TextToSpeechResponse: The response containing the generated speech.

        Raises:
            HTTPException: If there is an error during the HTTP request.
        """
        request = TextToSpeechRequest(text=text, lang=lang)   
        response = await HttpUtils.apost(
            request=request,
            response_model=TextToSpeechResponse,
            url=Config.TEXT_TO_SPEECH_SERVICE_ENDPOINT,
        )
        
        return response
