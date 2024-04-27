import asyncio
from typing import List

from core.config import Config
from models.persona import Persona
from utils.logger import log_decorator
from utils.http_utils import HttpUtils


class PersonaService:
    """
    A class that provides methods to interact with the Persona service.
    """

    @log_decorator
    @staticmethod
    async def aget_all() -> List[Persona]:
        """
        Retrieves all the personas from the Persona service.

        Returns:
            A list of Persona objects representing all the personas.
        """
        try:
            return await HttpUtils.get(
                Config.PERSONA_SERVICE_LIST_ENDPOINT,
                response_model=List[Persona],
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_all() -> List[Persona]:
        """
        Retrieves all the personas from the Persona service synchronously.

        Returns:
            A list of Persona objects representing all the personas.
        """
        return asyncio.run(PersonaService.aget_all())

    @log_decorator
    @staticmethod
    async def aget_all_names() -> List[str]:
        """
        Retrieves the names of all the personas from the Persona service.

        Returns:
            A list of strings representing the names of all the personas.
        """
        try:
            personas = await PersonaService.aget_all()
            return [persona.persona_name for persona in personas]
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def get_all_names() -> List[str]:
        """
        Retrieves the names of all the personas from the Persona service synchronously.

        Returns:
            A list of strings representing the names of all the personas.
        """
        return asyncio.run(PersonaService.aget_all_names())
