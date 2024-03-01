from typing import List

from core.config import Config
from utils.http_utils import HttpUtils
from models.common.list_response import ListResponse


class PersonaService:
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
