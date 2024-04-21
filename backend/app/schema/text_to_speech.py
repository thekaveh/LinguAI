from pydantic import BaseModel


class TextToSpeechRequest(BaseModel):
    """
    Represents a request for text-to-speech conversion.

    Attributes:
        text (str): The text to be converted to speech.
        lang (str, optional): The language of the text. Defaults to "en".
    """
    text: str
    lang: str = "en"


class TextToSpeechResponse(BaseModel):
    """
    Represents the response from the Text-to-Speech API.

    Attributes:
        audio (str): The generated audio file.
        lang (str, optional): The language of the generated audio file. Defaults to "en".
    """
    audio: str
    lang: str = "en"
