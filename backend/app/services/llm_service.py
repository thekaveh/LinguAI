from os import stat
from typing import List
from ollama import Client

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.schema.runnable import Runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import Config

class LLMService:
    @staticmethod
    def get_runnable(model: str) -> Runnable:
        if model.startswith("ollama-"):
            return ChatOpenAI(
                model=model[len("ollama-"):]
				, base_url=Config.OLLAMA_OPENAI_ENDPOINT
				, openai_api_key=Config.OLLAMA_OPENAI_API_KEY
			)
        elif model.startswith("openai-"):
            return ChatOpenAI(
                model=model[len("openai-"):]
				, base_url=Config.OPENAI_API_ENDPOINT
				, openai_api_key=Config.OPENAI_API_KEY
			)
        else:
            return None
        
    @staticmethod
    def list_models() -> List[str]:
        # return [f"ollama-{model['model']}" for model in Client(host=Config.OLLAMA_API_ENDPOINT).list()['models']] + ["openai-gpt-3.5-turbo", "openai-gpt-4"]
        return ["ollama-llama2:latest", "ollama-mistral:latest", "openai-gpt-3.5-turbo", "openai-gpt-4"]
    