import asyncio

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from models.embeddings_quiz import EmbeddingsQuizRequest, EmbeddingsQuizResponse


class EmbeddingsQuizService:
    @log_decorator
    @staticmethod
    async def agenerate(request: EmbeddingsQuizRequest) -> EmbeddingsQuizResponse:
        return await HttpUtils.apost(
            url=Config.EMBEDDINGS_QUIZ_GENERATE_SERVICE,
            request=request,
            response_model=EmbeddingsQuizResponse,
        )

    @log_decorator
    @staticmethod
    def generate(request: EmbeddingsQuizRequest) -> EmbeddingsQuizResponse:
        return asyncio.run(EmbeddingsQuizService.agenerate(request))
