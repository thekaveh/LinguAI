import asyncio
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from models.polyglot_puzzle import PolyglotPuzzleRequest, PolyglotPuzzleResponse


class PolyglotPuzzleService:
    """
    This class provides methods to interact with the embeddings quiz service.
    """

    @log_decorator
    @staticmethod
    async def agenerate(request: PolyglotPuzzleRequest) -> PolyglotPuzzleResponse:
        """
        Asynchronously generates an embeddings quiz using the provided request.

        Args:
            request (PolyglotPuzzleRequest): The request object containing the necessary data.

        Returns:
            PolyglotPuzzleResponse: The response object containing the generated quiz.
        """
        return await HttpUtils.apost(
            url=Config.POLYGLOT_PUZZLE_GENERATE_SERVICE,
            request=request,
            response_model=PolyglotPuzzleResponse,
        )

    @log_decorator
    @staticmethod
    def generate(request: PolyglotPuzzleRequest) -> PolyglotPuzzleResponse:
        """
        Generates an embeddings quiz using the provided request.

        Args:
            request (PolyglotPuzzleRequest): The request object containing the necessary data.

        Returns:
            PolyglotPuzzleResponse: The response object containing the generated quiz.
        """
        return asyncio.run(PolyglotPuzzleService.agenerate(request))
