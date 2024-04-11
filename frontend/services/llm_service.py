import asyncio
from typing import List

from models.llm import LLM
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils


class LLMService:
    @log_decorator
    @staticmethod
    async def aget_all() -> List[LLM]:
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_ALL_ENDPOINT, response_model=List[LLM]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_all() -> List[LLM]:
        return asyncio.run(LLMService.aget_all())

    @log_decorator
    @staticmethod
    async def aget_chat() -> List[LLM]:
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_CHAT_ENDPOINT, response_model=List[LLM]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_chat() -> List[LLM]:
        return asyncio.run(LLMService.aget_chat())

    @log_decorator
    @staticmethod
    async def aget_translate() -> List[LLM]:
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_TRANSLATE_ENDPOINT, response_model=List[LLM]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_translate() -> List[LLM]:
        return asyncio.run(LLMService.aget_translate())

    @log_decorator
    @staticmethod
    async def aget_vision() -> List[LLM]:
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_VISION_ENDPOINT, response_model=List[LLM]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_vision() -> List[LLM]:
        return asyncio.run(LLMService.aget_vision())

    @log_decorator
    @staticmethod
    async def aget_embeddings() -> List[LLM]:
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_EMBEDDINGS_ENDPOINT, response_model=List[LLM]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_embeddings() -> List[LLM]:
        return asyncio.run(LLMService.aget_embeddings())
