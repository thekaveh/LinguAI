from typing import List

from core.config import Config
from utils.http_utils import HttpUtils
from models.common.list_response import ListResponse


class LLMService:
    @staticmethod
    async def list_models() -> List[str]:
        try:
            return (
                await HttpUtils.get(
                    Config.LLM_SERVICE_LIST_MODELS_ENDPOINT, response_model=ListResponse
                )
            ).result
        except Exception as e:
            raise e

    @staticmethod
    async def list_vision_models() -> List[str]:
        try:
            return (
                await HttpUtils.get(
                    Config.LLM_SERVICE_LIST_VISION_MODELS_ENDPOINT,
                    response_model=ListResponse,
                )
            ).result
        except Exception as e:
            raise e
