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

    DEFAULT_LANGUAGE_TRANSLATION_MODEL = os.environ.get(
        "DEFAULT_LANGUAGE_TRANSLATION_MODEL", "gpt-3.5-turbo"
    )
    DEFAULT_PERSONA = os.environ.get("DEFAULT_PERSONA", "Neutral")
    DEFAULT_TEMPERATURE = os.environ.get("DEFAULT_TEMPERATURE", "0.0")

    VISION_MODELS = os.environ.get("VISION_MODELS", "")

    # Database configurations
    DB_PORT = os.getenv("DB_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "linguai_db")
    POSTGRES_DB_HOST = os.getenv("POSTGRES_DB_HOST", "db")
    POSTGRES_APP_USER = os.getenv("POSTGRES_APP_USER", "linguai_app")
    POSTGRES_APP_PASSWORD = os.getenv("POSTGRES_APP_PASSWORD", "linguai_app_pass")
    DATABASE_URL = f"postgresql://{POSTGRES_APP_USER}:{POSTGRES_APP_PASSWORD}@{POSTGRES_DB_HOST}:{DB_PORT}/{POSTGRES_DB}"
