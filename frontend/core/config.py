import os


class Config:
    BACKEND_ENDPOINT = os.environ.get("BACKEND_ENDPOINT", "")

    # Defaults for the frontend and for demo purposes
    DEFAULT_USER_NAME = os.environ.get("DEFAULT_USER_NAME", "")
    DEFAULT_SKILL_LEVEL = os.environ.get("DEFAULT_SKILL_LEVEL", "")
    DEFAULT_TEMPERATURE = os.environ.get("DEFAULT_TEMPERATURE", "")
    DEFAULT_PERSONA = os.environ.get("DEFAULT_PERSONA", "")
    DEFAULT_LANGUAGE_TRANSLATION_MODEL = os.environ.get(
        "DEFAULT_LANGUAGE_TRANSLATION_MODEL", ""
    )
    DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "")

    LLM_SERVICE_LIST_MODELS_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/llm/list_models"
    LLM_SERVICE_LIST_VISION_MODELS_ENDPOINT = (
        f"{BACKEND_ENDPOINT}/v1/llm/list_vision_models"
    )


    CHAT_SERVICE_ENDPOINT 			= f"{BACKEND_ENDPOINT}/v1/chat"
    PERSONA_SERVICE_LIST_ENDPOINT 	= f"{BACKEND_ENDPOINT}/v1/persona/list"
    USER_SERVICE_LIST_ENDPOINT 		= f"{BACKEND_ENDPOINT}/v1/users/list"
    USER_SERVICE_USERNAME_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/users/username/"    

    ADDRESS_SERVICE_LIST_ENDPOINT 	= f"{BACKEND_ENDPOINT}/v1/addresses/list"
    
    CONTENT_SERVICE_LIST_ENDPOINT 	= f"{BACKEND_ENDPOINT}/v1/contents/list"
    CONTENT_GEN_SERVICE_CONTENT_TOPIC_ENDPOINT 	= f"{BACKEND_ENDPOINT}/v1/content_gen/gen_by_content_topic"  
    REWRITE_CONTENT_SERVICE_ENDPOINT 	= f"{BACKEND_ENDPOINT}/v1/rewrite_content/"
    TOPIC_SERVICE_LIST_ENDPOINT 	= f"{BACKEND_ENDPOINT}/v1/topics/list"    
    SKILL_LEVEL_SERVICE_LIST_ENDPOINT= f"{BACKEND_ENDPOINT}/v1/skill_levels/list"   
    LANGUAGE_SERVICE_LIST_ENDPOINT= f"{BACKEND_ENDPOINT}/v1/languages/list"       
    REVIEW_WRITING_SERVICE_ENDPOINT 	= f"{BACKEND_ENDPOINT}/v1/review_writing/"
    

    # Logger
    FRONTEND_LOG_LEVEL = os.getenv("FRONTEND_LOG_LEVEL", "INFO")
    FRONTEND_LOGGER_NAME = os.getenv("FRONTEND_LOGGER_NAME", "LinguAI-FRONTEND")
    FRONTEND_LOG_FILE = os.getenv("FRONTEND_LOG_FILE", "/app/logs/front-app.log")
