from ollama import Client
from typing import List, Optional
from sqlmodel import Session, select, or_

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import Runnable
from langchain_community.chat_models import ChatOllama

from app.models.llm import LLM
from app.core.config import Config
from app.utils.logger import log_decorator
from app.services.crud_service import CRUDService


class LLMService(CRUDService[LLM]):
    @log_decorator
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @log_decorator
    def get_all(self) -> List[LLM]:
        """
        Retrieve all LLM models based on certain conditions.

        Returns:
            List[LLM]: A list of LLM models that match the specified conditions.

        Raises:
            Exception: If there is an error fetching the models.
        """
        try:
            query = select(LLM).where(LLM.is_active)

            conditions = []

            if Config.OPENAI_API_KEY:
                conditions.append((LLM.provider == "openai"))

            if Config.GROQ_API_KEY:
                conditions.append((LLM.provider == "groq"))

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
    def get_embeddings(self) -> List[LLM]:
        return sorted(
            [llm for llm in self.get_all() if llm.embeddings > 0],
            key=lambda llm: llm.embeddings,
        )

    @log_decorator
    def get_content(self) -> List[LLM]:
        return sorted(
            [llm for llm in self.get_all() if llm.content > 0],
            key=lambda llm: llm.content,
        )

    @log_decorator
    def get_structured_content(self) -> List[LLM]:
        return sorted(
            [llm for llm in self.get_all() if llm.structured_content > 0],
            key=lambda llm: llm.structured_content,
        )

    @log_decorator
    def get_vision(self) -> List[LLM]:
        return sorted(
            [llm for llm in self.get_all() if llm.vision > 0],
            key=lambda llm: llm.vision,
        )

    @log_decorator
    def get_by_id(self, id: int) -> Optional[LLM]:
        query = select(LLM).where(LLM.is_active).where(LLM.id == id)

        return self.db_session.exec(query).first()

    @log_decorator
    def get_by_name(self, name: str) -> Optional[LLM]:
        query = select(LLM).where(LLM.is_active).where(LLM.name == name)

        return self.db_session.exec(query).first()

    @log_decorator
    def get_chat_runnable(self, llm_id: int, temperature: float = 0) -> Runnable:
        """
        Returns a runnable object for chat based on the specified LLM ID and temperature.

        Args:
            llm_id (int): The ID of the LLM.
            temperature (float, optional): The temperature value for generating chat responses. Defaults to 0.

        Returns:
            Runnable: A runnable object for chat based on the specified LLM ID and temperature.

        Raises:
            Exception: If the LLM with the specified ID is not found or if the provider is not supported.
        """
        try:
            llm = self.get_by_id(id=llm_id)

            if not llm:
                raise Exception(f"LLM with id {llm_id} not found!")

            if llm.provider == "openai":
                return ChatOpenAI(
                    model=llm.name,
                    streaming=True,
                    temperature=temperature,
                    base_url=Config.OPENAI_API_ENDPOINT,
                    openai_api_key=Config.OPENAI_API_KEY,
                )
            elif llm.provider == "groq":
                return ChatGroq(
                    streaming=True,
                    model_name=llm.name,
                    temperature=temperature,
                    groq_api_key=Config.GROQ_API_KEY,
                    # groq_api_base=Config.GROQ_API_ENDPOINT,
                )
            elif llm.provider == "ollama":
                return ChatOllama(
                    model=llm.name,
                    streaming=True,
                    temperature=temperature,
                    base_url=Config.OLLAMA_API_ENDPOINT,
                )
            else:
                raise Exception(f"Provider {llm.provider} not supported!")
        except Exception as e:
            raise e

    @log_decorator
    def init_ollama(self) -> None:
        """
        Initializes the Ollama service by checking for required models and pulling them if necessary.

        Raises:
            Exception: If an error occurs during the initialization process.
        """
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
