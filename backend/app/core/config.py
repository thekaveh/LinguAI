import os
import json

class Config:
    OPENAI_API_KEY		: str 	= os.environ.get("OPENAI_API_KEY", "")
    LITELLM_API_KEY		: str 	= "NULL"
    
    OPENAI_API_ENDPOINT	: str 	= os.environ.get("OPENAI_API_ENDPOINT", "")
    LITELLM_API_ENDPOINT: str 	= os.environ.get("LITELLM_API_ENDPOINT", "")
    OLLAMA_API_ENDPOINT	: str 	= os.environ.get("OLLAMA_API_ENDPOINT", "")