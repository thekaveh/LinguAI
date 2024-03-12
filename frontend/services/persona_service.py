from typing import List

from core.config import Config
from models.persona import Persona
from utils.logger import log_decorator
from utils.http_utils import HttpUtils


class PersonaService:
    @log_decorator
    @staticmethod
    async def get_all() -> List[Persona]:
        try:
            return await HttpUtils.get(
                Config.PERSONA_SERVICE_LIST_ENDPOINT,
                response_model=List[Persona],
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
