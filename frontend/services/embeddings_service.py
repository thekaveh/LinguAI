import asyncio

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils

from models.embeddings import (
    EmbeddingsGetRequest,
    EmbeddingsGetResponse,
    EmbeddingsReduceRequest,
    EmbeddingsReduceResponse,
    EmbeddingsSimilaritiesRequest,
    EmbeddingsSimilaritiesResponse,
)


class EmbeddingsService:
    """
    A class that provides methods for interacting with the embeddings service.
    """

    @log_decorator
    @staticmethod
    async def aget(request: EmbeddingsGetRequest) -> EmbeddingsGetResponse:
        """
        Retrieves embeddings asynchronously.

        Args:
            request (EmbeddingsGetRequest): The request object.

        Returns:
            EmbeddingsGetResponse: The response object.
        """
        try:
            return await HttpUtils.apost(
                request=request,
                url=Config.EMBEDDINGS_SERVICE_GET_ENDPOINT,
                response_model=EmbeddingsGetResponse,
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get(request: EmbeddingsGetRequest) -> EmbeddingsGetResponse:
        """
        Retrieves embeddings.

        Args:
            request (EmbeddingsGetRequest): The request object.

        Returns:
            EmbeddingsGetResponse: The response object.
        """
        return asyncio.run(EmbeddingsService.aget(request))

    @log_decorator
    @staticmethod
    async def asimilarities(
        request: EmbeddingsSimilaritiesRequest,
    ) -> EmbeddingsSimilaritiesResponse:
        """
        Retrieves similarities between embeddings asynchronously.

        Args:
            request (EmbeddingsSimilaritiesRequest): The request object.

        Returns:
            EmbeddingsSimilaritiesResponse: The response object.
        """
        try:
            return await HttpUtils.apost(
                request=request,
                url=Config.EMBEDDINGS_SERVICE_SIMILARITIES_ENDPOINT,
                response_model=EmbeddingsSimilaritiesResponse,
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def similarities(
        request: EmbeddingsSimilaritiesRequest,
    ) -> EmbeddingsSimilaritiesResponse:
        """
        Retrieves similarities between embeddings.

        Args:
            request (EmbeddingsSimilaritiesRequest): The request object.

        Returns:
            EmbeddingsSimilaritiesResponse: The response object.
        """
        return asyncio.run(EmbeddingsService.asimilarities(request))

    @log_decorator
    @staticmethod
    async def areduce(request: EmbeddingsReduceRequest) -> EmbeddingsReduceResponse:
        """
        Reduces embeddings asynchronously.

        Args:
            request (EmbeddingsReduceRequest): The request object.

        Returns:
            EmbeddingsReduceResponse: The response object.
        """
        try:
            return await HttpUtils.apost(
                request=request,
                url=Config.EMBEDDINGS_SERVICE_REDUCE_ENDPOINT,
                response_model=EmbeddingsReduceResponse,
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def reduce(request: EmbeddingsReduceRequest) -> EmbeddingsReduceResponse:
        """
        Reduces embeddings.

        Args:
            request (EmbeddingsReduceRequest): The request object.

        Returns:
            EmbeddingsReduceResponse: The response object.
        """
        return asyncio.run(EmbeddingsService.areduce(request))
