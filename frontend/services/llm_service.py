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
