import asyncio
from typing import List
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.language import Language as LanguageSchema


class LanguageService:
    """
    This class provides methods to interact with the language service API.
    """

    @log_decorator
    @staticmethod
    async def list() -> List[LanguageSchema]:
        """
        Fetches the list of languages from the language service API.

        Returns:
            A list of LanguageSchema objects representing the languages.
        """
        try:
            # Adjust Config.LANGUAGE_SERVICE_LIST_ENDPOINT to your actual configuration
            languages_list = await HttpUtils.get(
                Config.LANGUAGE_SERVICE_LIST_ENDPOINT,
                response_model=List[LanguageSchema],
            )
            return languages_list
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    def list_sync() -> List[LanguageSchema]:
        """
        Synchronously fetches the list of languages from the language service API.

        Returns:
            A list of LanguageSchema objects representing the languages.
        """
        return asyncio.run(LanguageService.list())

    @log_decorator
    @staticmethod
    async def get_language_by_name(language_name: str) -> LanguageSchema:
        """
        Fetches a language by its name from the language service API.

        Args:
            language_name: The name of the language to fetch.

        Returns:
            A LanguageSchema object representing the language.

        Raises:
            Exception: If the language fetching fails.
        """
        try:
            url = f"{Config.LANGUAGE_SERVICE_GET_ENDPOINT}/{language_name}"
            return await HttpUtils.get(
                url,
                response_model=LanguageSchema,
            )
        except Exception as e:
            raise Exception(f"Failed to fetch language '{language_name}: {e}")
