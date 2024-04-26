from typing import List
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.topic import Topic as TopicSchema


class TopicService:
    """
    Service class for managing topics.
    """

    @log_decorator
    @staticmethod
    async def list() -> List[TopicSchema]:
        """
        Retrieves a list of topics.

        Returns:
            A list of TopicSchema objects representing the topics.
        """
        try:
            # Adjust Config.TOPICS_SERVICE_LIST_ENDPOINT to your actual configuration
            topics_list = await HttpUtils.get(
                Config.TOPIC_SERVICE_LIST_ENDPOINT, response_model=List[TopicSchema]
            )
            return topics_list
        except Exception as e:
            raise e
