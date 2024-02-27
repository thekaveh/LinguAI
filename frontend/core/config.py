import os


class Config:
    BACKEND_ENDPOINT = os.environ.get("BACKEND_ENDPOINT", "")

    CHAT_SERVICE_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/chat"

    LLM_SERVICE_LIST_MODELS_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/llm/list_models"
    LLM_SERVICE_LIST_VISION_MODELS_ENDPOINT = (
        f"{BACKEND_ENDPOINT}/v1/llm/list_vision_models"
    )

    PERSONA_SERVICE_LIST_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/persona/list"
