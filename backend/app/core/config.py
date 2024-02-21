import os
import json


class Config:
    """
    Configuration class for the application.
    """

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODELS = os.environ.get("OPENAI_MODELS", "")
    OLLAMA_OPENAI_API_KEY = "ollama"
    OPENAI_API_ENDPOINT = os.environ.get("OPENAI_API_ENDPOINT", "")
    OLLAMA_API_ENDPOINT = os.environ.get("OLLAMA_API_ENDPOINT", "")
    OLLAMA_OPENAI_ENDPOINT = OLLAMA_API_ENDPOINT + "/v1"
