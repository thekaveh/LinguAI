from ollama import Client
from typing import List, Optional
from sqlmodel import Session, select, or_

from langchain_openai import ChatOpenAI
from langchain.schema.runnable import Runnable
from langchain_community.chat_models import ChatOllama
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings

from app.models.llm import LLM
from app.core.config import Config
from app.utils.logger import log_decorator
from app.services.crud_service import CRUDService
from app.models.embeddings import EmbeddingsGetRequest, EmbeddingsGetResponse


class LLMService(CRUDService[LLM]):
    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @log_decorator
    def get_all(self) -> List[LLM]:
        try:
            query = select(LLM).where(LLM.is_active)

            conditions = []

            if Config.OPENAI_API_KEY:
                conditions.append((LLM.provider == "openai"))
            if Config.OLLAMA_API_ENDPOINT:
                pulled_ollama_models = [
                    model["model"]
                    for model in Client(host=Config.OLLAMA_API_ENDPOINT).list()[
                        "models"
                    ]
                ]
                conditions.append(
                    (LLM.provider == "ollama") & (LLM.name.in_(pulled_ollama_models))
                )

            if conditions:
                query = query.where(or_(*conditions))
            else:
                query = query.where(LLM.provider == None)

            return self.db_session.exec(query).all()
        except Exception as e:
            raise Exception("Error fetching models") from e

    @log_decorator
    def get_by_name(self, name: str) -> Optional[LLM]:
        query = select(LLM).where(LLM.is_active).where(LLM.name == name)

        return self.db_session.exec(query).first()

    @log_decorator
    def get_chat_runnable(self, model: str, temperature: float = 0) -> Runnable:
        try:
            llm = self.get_by_name(model)

            if not llm:
                raise Exception(f"Model {model} not found!")

            if llm.provider == "openai":
                return ChatOpenAI(
                    model=model,
                    streaming=True,
                    temperature=temperature,
                    base_url=Config.OPENAI_API_ENDPOINT,
                    openai_api_key=Config.OPENAI_API_KEY,
                )
            elif llm.provider == "ollama":
                return ChatOllama(
                    model=model,
                    streaming=True,
                    temperature=temperature,
                    base_url=Config.OLLAMA_API_ENDPOINT,
                )
            else:
                raise Exception(f"Provider {llm.provider} not supported!")
        except Exception as e:
            raise e

    @log_decorator
    def get_embeddings(self, request: EmbeddingsGetRequest) -> EmbeddingsGetResponse:
        try:
            llm = self.get_by_name(request.model)

            if not llm:
                raise Exception(f"Model {request.model} not found!")

            print(request.model)
            print(request.texts)

            print(llm)

            if llm.provider == "openai":
                embeddings = OpenAIEmbeddings(
                    model=llm.name,
                    base_url=Config.OPENAI_API_ENDPOINT,
                    openai_api_key=Config.OPENAI_API_KEY,
                )
            elif llm.provider == "ollama":
                print("ollama")
                embeddings = OllamaEmbeddings(
                    model=llm.name,
                    base_url=Config.OLLAMA_API_ENDPOINT
                )
            else:
                raise Exception(f"Provider {llm.provider} not supported!")

            return embeddings.embed_documents(request.texts)
        except Exception as e:
            raise e

    @log_decorator
    def init_ollama(self) -> None:
        try:
            if Config.OLLAMA_API_ENDPOINT:
                query = select(LLM).where(LLM.is_active).where(LLM.provider == "ollama")
                required_ollama_model_names = [
                    m.name for m in self.db_session.exec(query).all()
                ]

                ollama_client = Client(host=Config.OLLAMA_API_ENDPOINT)
                exiting_ollama_model_names = [
                    model["model"] for model in ollama_client.list()["models"]
                ]

                diff_model_names = [
                    model_name
                    for model_name in required_ollama_model_names
                    if model_name not in exiting_ollama_model_names
                ]
                for model_name in diff_model_names:
                    ollama_client.pull(model=model_name, stream=False)
        except Exception as e:
            raise e
