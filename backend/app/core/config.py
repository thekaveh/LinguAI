import os
import json

class Config:
    OPENAI_API_KEY			: str 	= os.environ.get("OPENAI_API_KEY", "")
    OLLAMA_OPENAI_API_KEY	: str 	= "ollama"
    
    OPENAI_API_ENDPOINT		: str 	= os.environ.get("OPENAI_API_ENDPOINT", "")
    OLLAMA_API_ENDPOINT		: str 	= os.environ.get("OLLAMA_API_ENDPOINT", "")
    OLLAMA_OPENAI_ENDPOINT	: str 	= OLLAMA_API_ENDPOINT + "/v1"