from typing import List

from core.config import Config
from utils.http_utils import HttpUtils
from models.messages.list_message import ListMessage


class PersonaService:
    @staticmethod
    async def list() -> List[str]:
        try:
            return (
                await HttpUtils.get(
                    Config.PERSONA_SERVICE_LIST_ENDPOINT, response_model=ListMessage
                )
            ).result
        except Exception as e:
            raise e
