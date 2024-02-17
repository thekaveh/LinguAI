import os

class Config:
    BACKEND_ENDPOINT 				= os.environ.get("BACKEND_ENDPOINT", "http://backend:8001")

    CHAT_SERVICE_ENDPOINT 			= f"{BACKEND_ENDPOINT}/v1/chat"
    LLM_SERVICE_LIST_ENDPOINT 		= f"{BACKEND_ENDPOINT}/v1/llm/list"
    PERSONA_SERVICE_LIST_ENDPOINT 	= f"{BACKEND_ENDPOINT}/v1/persona/list"