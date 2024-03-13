from typing import List

from core.config import Config
from models.language import Language
from utils.logger import log_decorator
from utils.http_utils import HttpUtils


class LanguageService:
    @log_decorator
    @staticmethod
    async def get_all() -> List[Language]:
        try:
            languages_list = await HttpUtils.get(
                Config.LANGUAGE_SERVICE_LIST_ENDPOINT,
                response_model=List[Language],
            )
            return languages_list
        except Exception as e:
            raise e
