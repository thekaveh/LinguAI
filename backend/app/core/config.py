import os


class Config:
    """
    Configuration class for the application.
    """

    # OpenAI
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_API_ENDPOINT = os.environ.get("OPENAI_API_ENDPOINT", "")

    # Groq
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_API_ENDPOINT = os.environ.get("GROQ_API_ENDPOINT", "")

    # Ollama
    OLLAMA_OPENAI_API_KEY = "ollama"
    OLLAMA_API_ENDPOINT = os.environ.get("OLLAMA_API_ENDPOINT", "")
    OLLAMA_OPENAI_API_ENDPOINT = OLLAMA_API_ENDPOINT + "/v1"

    DEFAULT_LANGUAGE_TRANSLATION_MODEL = os.environ.get(
        "DEFAULT_LANGUAGE_TRANSLATION_MODEL", "gpt-3.5-turbo"
    )
    DEFAULT_PERSONA = os.environ.get("DEFAULT_PERSONA", "Neutral")
    DEFAULT_TEMPERATURE = os.environ.get("DEFAULT_TEMPERATURE", "0.0")

    # Database configurations
    DB_PORT = os.getenv("DB_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "linguai_db")
    POSTGRES_DB_HOST = os.getenv("POSTGRES_DB_HOST", "db")
    POSTGRES_APP_USER = os.getenv("POSTGRES_APP_USER", "linguai_app")
    POSTGRES_APP_PASSWORD = os.getenv("POSTGRES_APP_PASSWORD", "linguai_app_pass")
    DATABASE_URL = f"postgresql://{POSTGRES_APP_USER}:{POSTGRES_APP_PASSWORD}@{POSTGRES_DB_HOST}:5432/{POSTGRES_DB}"

    # Logger
    BACKEND_LOG_LEVEL = os.getenv("BACKEND_LOG_LEVEL", "INFO")
    BACKEND_LOGGER_NAME = os.getenv("BACKEND_LOGGER_NAME", "LinguAI-BACKEND")
    BACKEND_LOG_FILE = os.getenv("BACKEND_LOG_FILE", "/app/logs/backend-app.log")
