import base64
from gtts import gTTS
from io import BytesIO

from app.utils.logger import log_decorator
from app.schema.text_to_speech import TextToSpeechRequest, TextToSpeechResponse


class TextToSpeechService:
    """
    A class that provides text-to-speech functionality.

    Methods:
        generate(request: TextToSpeechRequest) -> TextToSpeechResponse: Generates audio from the given text.
    """

    @log_decorator
    def __init__(self):
        pass

    @log_decorator
    def generate(self, request: TextToSpeechRequest) -> TextToSpeechResponse:
        """
        Generates audio from the given text.

        Args:
            request (TextToSpeechRequest): The request object containing the text and language.

        Returns:
            TextToSpeechResponse: The response object containing the generated audio and language.
        """
        tts = gTTS(text=request.text, lang=request.lang)

        with BytesIO() as audio_buffer:
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode("utf-8")
            audio_data = f"data:audio/mpeg;base64,{audio_base64}"

            return TextToSpeechResponse(audio=audio_data, lang=request.lang)
