from ollama import Client

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import Config

class LlmService:
    def __init__(self):
        pass
    
    def get_llm(self, llm_name: str):
        if llm_name.startswith("ollama/"):
            return Ollama(
				model=llm_name.split("/")[1]
				, base_url=Config.OLLAMA_API_ENDPOINT
			)
        elif llm_name.startswith("openai/"):
            return ChatOpenAI(
                model=llm_name.split("/")[1]
				, base_url=Config.OPENAI_API_ENDPOINT
				, openai_api_key=Config.OPENAI_API_KEY
			)
        elif llm_name == "litellm":
            return ChatOpenAI(
				base_url=Config.LITELLM_API_ENDPOINT
				, openai_api_key=Config.LITELLM_API_KEY
			)
        else:
            return None
    
    def list_llms(self):
        return [f"ollama/{model['model']}" for model in Client(host=Config.OLLAMA_API_ENDPOINT).list()['models']] + ["openai/gpt-3.5-turbo", "openai/gpt-4", "litellm"]