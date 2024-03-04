from typing import List

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.list_response import ListResponse


class PersonaService:
    @log_decorator
    @staticmethod
    async def list() -> List[str]:
        try:
            return (
                await HttpUtils.get(
                    Config.PERSONA_SERVICE_LIST_ENDPOINT, response_model=ListResponse
                )
            ).result
        except Exception as e:
            raise e
