from typing import List

from core.config import Config
from utils.http_utils import HttpUtils
from models.common.list_response import ListResponse
from models.schema.content import Content as ContentSchema


class ContentService:
    @staticmethod
    async def list() -> List[ContentSchema]:
        try:
            # Directly expecting a list of ContentSchema objects
            content_list = await HttpUtils.get(
                Config.CONTENT_SERVICE_LIST_ENDPOINT,
                response_model=List[ContentSchema]
            )
            return content_list
        except Exception as e:
            raise e

