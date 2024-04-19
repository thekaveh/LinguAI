from fastapi import APIRouter, HTTPException

from app.utils.logger import log_decorator
from app.services.text_to_speech_service import TextToSpeechService
from app.schema.text_to_speech import TextToSpeechRequest, TextToSpeechResponse

router = APIRouter()


@log_decorator
@router.post("/text_to_speech")
async def chat(request: TextToSpeechRequest) -> TextToSpeechResponse:
    """
    Generate speech from text.

    Args:
        request (TextToSpeechRequest): The request object containing the text to convert to speech.

    Returns:
        TextToSpeechResponse: The response object containing the generated speech.

    Raises:
        HTTPException: If an error occurs during the speech generation process.
    """
    try:
        service = TextToSpeechService()
        return service.generate(request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
