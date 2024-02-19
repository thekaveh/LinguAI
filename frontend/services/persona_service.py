from typing import List

from core.config import Config
from models.list_res import ListRes
from utils.http_utils import HttpUtils

class PersonaService:
    @staticmethod
    async def list() -> List[str]:
        try:
            return (await HttpUtils.get(Config.PERSONA_SERVICE_LIST_ENDPOINT, response_model=ListRes)).result
        except Exception as e:
            raise e