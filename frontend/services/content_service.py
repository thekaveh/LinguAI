from typing import List

from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.content import Content as ContentSchema


class ContentService:
    """
    This class provides methods to interact with the content service.
    """

    @log_decorator
    @staticmethod
    async def list() -> List[ContentSchema]:
        """
        Retrieves a list of content from the content service.

        Returns:
            A list of ContentSchema objects.
        Raises:
            Exception: If an error occurs while retrieving the content.
        """
        try:
            # Directly expecting a list of ContentSchema objects
            content_list = await HttpUtils.get(
                Config.CONTENT_SERVICE_LIST_ENDPOINT, response_model=List[ContentSchema]
            )
            return content_list
        except Exception as e:
            raise e
