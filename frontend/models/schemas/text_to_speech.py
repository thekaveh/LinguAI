from pydantic import BaseModel


class TextToSpeechRequest(BaseModel):
    text: str
    lang: str = "en"


class TextToSpeechResponse(BaseModel):
    audio: str
    lang: str = "en"
