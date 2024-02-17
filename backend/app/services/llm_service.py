from typing import List
from ollama import Client

from langchain_openai import ChatOpenAI
from langchain.schema.runnable import Runnable

from app.core.config import Config

class LLMService:
    @staticmethod
    def get_runnable(model: str, temperature: float = 0) -> Runnable:
        try:
            if model.startswith("gpt-"):
                return ChatOpenAI(
					model=model
					, streaming=True
					, temperature=temperature
					, base_url=Config.OPENAI_API_ENDPOINT
					, openai_api_key=Config.OPENAI_API_KEY
				)
            else:
                return ChatOpenAI(
					model=model
					, streaming=True
					, temperature=temperature
					, base_url=Config.OLLAMA_OPENAI_ENDPOINT
					, openai_api_key=Config.OLLAMA_OPENAI_API_KEY
				)
        except:
            raise Exception(f"Model {model} not found")

    @staticmethod
    def list_models() -> List[str]:
        try:
            return [f"{model['model']}" for model in Client(host=Config.OLLAMA_API_ENDPOINT).list()['models']] + ["gpt-3.5-turbo", "gpt-4"]
        except:
            raise Exception("Error fetching models")