from typing import List
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.language import Language as LanguageSchema


class LanguageService:
    @log_decorator
    @staticmethod
    async def list() -> List[LanguageSchema]:
        try:
            # Adjust Config.LANGUAGE_SERVICE_LIST_ENDPOINT to your actual configuration
            languages_list = await HttpUtils.get(
                Config.LANGUAGE_SERVICE_LIST_ENDPOINT, response_model=List[LanguageSchema]
            )
            return languages_list
        except Exception as e:
            raise e