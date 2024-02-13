from ollama import Client

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import Config

class LLMService:
    def __init__(self):
        # for model in ["llama2:latest", "mistral:latest"]:
        #     Client(host=Config.OLLAMA_API_ENDPOINT).pull(model)
        pass
    
    def get(self, model: str):
        if model.startswith("ollama-"):
            return ChatOpenAI(
                model=model[len("ollama-"):]
				, openai_api_key="ollama"
				, base_url=Config.OLLAMA_API_ENDPOINT + "/v1"
			)
        elif model.startswith("openai-"):
            return ChatOpenAI(
                model=model[len("openai-"):]
				, base_url=Config.OPENAI_API_ENDPOINT
				, openai_api_key=Config.OPENAI_API_KEY
			)
        elif model == "litellm":
            return ChatOpenAI(
				base_url=Config.LITELLM_API_ENDPOINT
				, openai_api_key=Config.LITELLM_API_KEY
			)
        else:
            return None
    
    def list(self):
        # return [f"ollama-{model['model']}" for model in Client(host=Config.OLLAMA_API_ENDPOINT).list()['models']] + ["openai-gpt-3.5-turbo", "openai-gpt-4"]
        return ["ollama-llama2:latest", "ollama-mistral:latest", "openai-gpt-3.5-turbo", "openai-gpt-4"]
    