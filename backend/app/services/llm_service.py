from typing import List
from ollama import Client

from langchain_openai import ChatOpenAI
from langchain.schema.runnable import Runnable
from langchain_community.chat_models import ChatOllama

from app.core.config import Config


class LLMService:
    @staticmethod
    def get_chat_runnable(model: str, temperature: float = 0) -> Runnable:
        try:
            if model.startswith("gpt-"):
                return ChatOpenAI(
                    model=model,
                    streaming=True,
                    temperature=temperature,
                    base_url=Config.OPENAI_API_ENDPOINT,
                    openai_api_key=Config.OPENAI_API_KEY,
                )
            else:
                # return ChatOpenAI(
                #     model=model,
                #     streaming=True,
                #     temperature=temperature,
                #     base_url=Config.OLLAMA_OPENAI_API_ENDPOINT,
                #     openai_api_key=Config.OLLAMA_OPENAI_API_KEY,
                # )
                return ChatOllama(
                    model=model,
                    streaming=True,
                    temperature=temperature,
                    base_url=Config.OLLAMA_API_ENDPOINT,
                )
        except:
            raise Exception(f"Model {model} not found")

    @staticmethod
    def list_models() -> List[str]:
        """
        A static method to list models and return a list of strings.
        """

        try:
            models = []

            if Config.OLLAMA_API_ENDPOINT:
                ollama_models = [
                    f"{model['model']}"
                    for model in Client(host=Config.OLLAMA_API_ENDPOINT).list()[
                        "models"
                    ]
                ]
                models.extend(ollama_models)

            if Config.OPENAI_API_KEY:
                openai_models = Config.OPENAI_MODELS.split()
                models.extend(openai_models)

            return models
        except Exception as e:
            raise Exception("Error fetching models") from e

    @staticmethod
    def list_vision_models() -> List[str]:
        try:
            vision_models = []

            for model in LLMService.list_models():
                if model in Config.VISION_MODELS.split():
                    vision_models.append(model)

            return vision_models
        except Exception as e:
            raise Exception("Error fetching models") from e
