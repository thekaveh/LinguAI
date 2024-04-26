import asyncio
from typing import List

from models.llm import LLM
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils


class LLMService:
    """
    This class provides methods to interact with the LLM service.
    """

    @log_decorator
    @staticmethod
    async def aget_all() -> List[LLM]:
        """
        Retrieves all LLM objects asynchronously.

        Returns:
            A list of LLM objects.
        """
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_ALL_ENDPOINT, response_model=List[LLM]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_all() -> List[LLM]:
        """
        Retrieves all LLM objects synchronously.

        Returns:
            A list of LLM objects.
        """
        return asyncio.run(LLMService.aget_all())

    @log_decorator
    @staticmethod
    async def aget_content() -> List[LLM]:
        """
        Retrieves the content of LLM objects asynchronously.

        Returns:
            A list of LLM objects.
        """
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_CONTENT_ENDPOINT, response_model=List[LLM]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_content() -> List[LLM]:
        """
        Retrieves the content of LLM objects synchronously.

        Returns:
            A list of LLM objects.
        """
        return asyncio.run(LLMService.aget_content())

    @log_decorator
    @staticmethod
    async def aget_structured_content() -> List[LLM]:
        """
        Retrieves the structured content of LLM objects asynchronously.

        Returns:
            A list of LLM objects.
        """
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
        """
        Retrieves the structured content of LLM objects synchronously.

        Returns:
            A list of LLM objects.
        """
        return asyncio.run(LLMService.aget_structured_content())

    @log_decorator
    @staticmethod
    async def aget_vision() -> List[LLM]:
        """
        Retrieves the vision of LLM objects asynchronously.

        Returns:
            A list of LLM objects.
        """
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_VISION_ENDPOINT, response_model=List[LLM]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_vision() -> List[LLM]:
        """
        Retrieves the vision of LLM objects synchronously.

        Returns:
            A list of LLM objects.
        """
        return asyncio.run(LLMService.aget_vision())

    @log_decorator
    @staticmethod
    async def aget_embeddings() -> List[LLM]:
        """
        Retrieves the embeddings of LLM objects asynchronously.

        Returns:
            A list of LLM objects.
        """
        try:
            return await HttpUtils.get(
                Config.LLM_SERVICE_GET_EMBEDDINGS_ENDPOINT, response_model=List[LLM]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_embeddings() -> List[LLM]:
        """
        Retrieves the embeddings of LLM objects synchronously.

        Returns:
            A list of LLM objects.
        """
        return asyncio.run(LLMService.aget_embeddings())
