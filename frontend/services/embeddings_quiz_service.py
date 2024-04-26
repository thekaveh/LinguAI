import asyncio
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from models.embeddings_quiz import EmbeddingsQuizRequest, EmbeddingsQuizResponse

class EmbeddingsQuizService:
    """
    This class provides methods to interact with the embeddings quiz service.
    """

    @log_decorator
    @staticmethod
    async def agenerate(request: EmbeddingsQuizRequest) -> EmbeddingsQuizResponse:
        """
        Asynchronously generates an embeddings quiz using the provided request.

        Args:
            request (EmbeddingsQuizRequest): The request object containing the necessary data.

        Returns:
            EmbeddingsQuizResponse: The response object containing the generated quiz.
        """
        return await HttpUtils.apost(
            url=Config.EMBEDDINGS_QUIZ_GENERATE_SERVICE,
            request=request,
            response_model=EmbeddingsQuizResponse,
        )

    @log_decorator
    @staticmethod
    def generate(request: EmbeddingsQuizRequest) -> EmbeddingsQuizResponse:
        """
        Generates an embeddings quiz using the provided request.

        Args:
            request (EmbeddingsQuizRequest): The request object containing the necessary data.

        Returns:
            EmbeddingsQuizResponse: The response object containing the generated quiz.
        """
        return asyncio.run(EmbeddingsQuizService.agenerate(request))
