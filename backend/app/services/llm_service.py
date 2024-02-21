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
        """
        A static method to list models and return a list of strings.
        
        """
        try:
            # Fetch models from OLLAMA_API_ENDPOINT
            models = [f"{model['model']}" for model in Client(host=Config.OLLAMA_API_ENDPOINT).list()['models']]
            # Check if OPENAI_API_KEY is not empty
            if Config.OPENAI_API_KEY:
                # If OPENAI_API_KEY is not empty, split the OPENAI_API_MODEL_LIST string
                openai_models = Config.OPENAI_MODEL_LIST.split()
                # Add the models specified in OPENAI_MODEL_LIST to the list
                models.extend(openai_models)
            else:
                # If OPENAI_API_KEY is empty, add an empty string to the list
                models.append("")
            return models
        except Exception as e:
            raise Exception("Error fetching models") from e