from typing import List, Callable

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.text_to_speech import TextToSpeechRequest, TextToSpeechResponse


class TextToSpeechService:
    @log_decorator
    @staticmethod
    async def agenerate(text: str, lang: str) -> TextToSpeechResponse:
        request = TextToSpeechRequest(text=text, lang=lang)   
        response = await HttpUtils.apost(
			request=request,
			response_model=TextToSpeechResponse,
			url=Config.TEXT_TO_SPEECH_SERVICE_ENDPOINT,
		)
        
        return response
