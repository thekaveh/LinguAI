import os


class Config:
    """
    Configuration class for the application.
    """

    # OpenAI
    OPENAI_MODELS = os.environ.get("OPENAI_MODELS", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_API_ENDPOINT = os.environ.get("OPENAI_API_ENDPOINT", "")

    # Ollama
    OLLAMA_OPENAI_API_KEY = "ollama"
    OLLAMA_API_ENDPOINT = os.environ.get("OLLAMA_API_ENDPOINT", "")
    OLLAMA_OPENAI_API_ENDPOINT = OLLAMA_API_ENDPOINT + "/v1"
    
    VISION_MODELS = os.environ.get("VISION_MODELS", "")