from typing import List

from core.config import Config
from utils.http_utils import HttpUtils
from models.llm_list_res import LLMListRes

class LLMService:
    @staticmethod
    async def list() -> List[str]:
        try:
            return (await HttpUtils.get(Config.LLM_SERVICE_LIST_ENDPOINT, response_model=LLMListRes)).result
        except Exception as e:
            raise e