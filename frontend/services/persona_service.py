from typing import List

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.persona import Persona as PersonaSchema


class PersonaService:
    @log_decorator
    @staticmethod
    async def get_all() -> List[PersonaSchema]:
        try:
            return await HttpUtils.get(
                Config.PERSONA_SERVICE_LIST_ENDPOINT,
                response_model=List[PersonaSchema],
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    async def get_all_names() -> List[str]:
        try:
            personas = await PersonaService.get_all()
            return [persona.persona_name for persona in personas]
        except Exception as e:
            raise e
