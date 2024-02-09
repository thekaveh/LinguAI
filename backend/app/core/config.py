import os

class Config:
    LLM_API_KEY_OPENAI	: str = os.environ.get("OPENAI_LLM_API_KEY", "")
    LLM_API_KEY_LOCAL	: str = "NULL"
    
    LLM_ENDPOINT_OPENAI	: str = os.environ.get("OPENAI_LLM_API_ENDPOINT", "http://llm:5000")
    LLM_ENDPOINT_LOCAL	: str = os.environ.get("LOCAL_LLM_API_ENDPOINT", "http://llm:5001")

config = Config()