import os


class Config:
    BACKEND_ENDPOINT = os.environ.get("BACKEND_ENDPOINT", "")
    # Use this to run tests locally
    # BACKEND_ENDPOINT = "http://localhost:50003"

    # Defaults for the frontend and for demo purposes
    # DEFAULT_USER_NAME = os.environ.get("DEFAULT_USER_NAME", "")
    DEFAULT_SKILL_LEVEL = os.environ.get("DEFAULT_SKILL_LEVEL", "")
    DEFAULT_TEMPERATURE = os.environ.get("DEFAULT_TEMPERATURE", "")
    DEFAULT_PERSONA = os.environ.get("DEFAULT_PERSONA", "")
    DEFAULT_LANGUAGE_TRANSLATION_MODEL = os.environ.get(
        "DEFAULT_LANGUAGE_TRANSLATION_MODEL", ""
    )
    DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "")

    LLM_SERVICE_GET_ALL_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/llms/"

    CHAT_SERVICE_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/chat"
    PERSONA_SERVICE_LIST_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/personas/"

    CONTENT_SERVICE_LIST_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/contents/list"
    CONTENT_GEN_SERVICE_CONTENT_TOPIC_ENDPOINT = (
        f"{BACKEND_ENDPOINT}/v1/content_gen/gen_by_content_topic"
    )

    # Logger
    FRONTEND_LOG_LEVEL = os.getenv("FRONTEND_LOG_LEVEL", "INFO")
    FRONTEND_LOGGER_NAME = os.getenv("FRONTEND_LOGGER_NAME", "LinguAI-FRONTEND")
    FRONTEND_LOG_FILE = os.getenv("FRONTEND_LOG_FILE", "/app/logs/front-app.log")

    LANGUAGE_SERVICE_LIST_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/languages/list"
    REWRITE_CONTENT_SERVICE_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/rewrite_content/"
    REVIEW_WRITING_SERVICE_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/review_writing/"

    SKILL_LEVEL_SERVICE_LIST_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/skill_levels/list"

    TOPIC_SERVICE_LIST_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/topics/list"

    USER_SERVICE_LIST_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/users/list"
    USER_SERVICE_USERNAME_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/users/username/"

    TEXT_TO_SPEECH_SERVICE_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/text_to_speech"

    USER_SERVICE_AUTHENTICATE_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/users/authenticate"
    USER_SERVICE_CREATE_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/users/"

    USER_CONTENT_SERVICE_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/user-contents/"
    USER_CONTENT_SERVICE_SEARCH_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/user-contents/search"
