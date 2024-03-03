from typing import List
from core.config import Config
from utils.http_utils import HttpUtils
# Assuming TopicSchema is defined in model.schema.topic
from models.schema.topic import Topic as TopicSchema

class TopicService:
    @staticmethod
    async def list() -> List[TopicSchema]:
        try:
            # Adjust Config.TOPICS_SERVICE_LIST_ENDPOINT to your actual configuration
            topics_list = await HttpUtils.get(
                Config.TOPIC_SERVICE_LIST_ENDPOINT,
                response_model=List[TopicSchema]
            )
            return topics_list
        except Exception as e:
            raise e
