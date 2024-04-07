from typing import List
from core.config import Config
from schema.user_content import UserContentBase, UserContentSearch, UserContent
from utils.http_utils import HttpUtils
from utils.logger import log_decorator
import logging

class UserContentService:
    logger=logging.getLogger(Config.FRONTEND_LOGGER_NAME)
    @log_decorator
    @staticmethod
    async def create_user_content(user_content: UserContentBase) -> UserContent:
        try:
            created_user_content = await HttpUtils.apost(
                Config.USER_CONTENT_SERVICE_ENDPOINT,  # This should be the full URL to your endpoint
                user_content,
                response_model=UserContent
            )
            return created_user_content
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    async def search_user_contents(search_params: UserContentSearch) -> List[UserContent]:
        try:
            user_contents = await HttpUtils.apost(
                Config.USER_CONTENT_SERVICE_SEARCH_ENDPOINT,
                search_params,
                response_model=List[UserContent]
            )
            return user_contents
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    async def delete_user_content(content_id: int) -> dict:
        UserContentService.logger.info(f"Deleting content with ID: {content_id}")
        try:
            response = await HttpUtils.delete(
                f"{Config.USER_CONTENT_SERVICE_ENDPOINT}{content_id}", 
            )
            return {"message": "Content deleted successfully"}
        except Exception as e:
            raise e
