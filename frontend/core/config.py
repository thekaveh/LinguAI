import os

class Config:
    BACKEND_ENDPOINT = os.environ.get("BACKEND_ENDPOINT", "http://backend:8001")

    LLM_SERVICE_CHAT_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/chat"
    LLM_SERVICE_LIST_ENDPOINT = f"{BACKEND_ENDPOINT}/v1/llm/list"