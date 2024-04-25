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
    async def aget_content() -> List[LLM]:
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_CONTENT_ENDPOINT, response_model=List[LLM]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_content() -> List[LLM]:
        return asyncio.run(LLMService.aget_content())

    @log_decorator
    @staticmethod
    async def aget_structured_content() -> List[LLM]:
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_STRUCTURED_CONTENT_ENDPOINT,
                response_model=List[LLM],
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_structured_content() -> List[LLM]:
        return asyncio.run(LLMService.aget_structured_content())

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
