from typing import List
from core.config import Config
from schema.user_content import UserContentBase, UserContentSearch, UserContent
from utils.http_utils import HttpUtils
from utils.logger import log_decorator
import logging

class UserContentService:
    """
    This class provides methods to interact with user content.
    """

    logger = logging.getLogger(Config.FRONTEND_LOGGER_NAME)

    @log_decorator
    @staticmethod
    async def create_user_content(user_content: UserContentBase) -> UserContent:
        """
        Creates a new user content.

        Args:
            user_content (UserContentBase): The user content to create.

        Returns:
            UserContent: The created user content.

        Raises:
            Exception: If an error occurs while creating the user content.
        """
        try:
            created_user_content = await HttpUtils.apost(
                Config.USER_CONTENT_SERVICE_ENDPOINT,
                user_content,
                response_model=UserContent
            )
            return created_user_content
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    async def search_user_contents(search_params: UserContentSearch) -> List[UserContent]:
        """
        Searches for user contents based on the provided search parameters.

        Args:
            search_params (UserContentSearch): The search parameters.

        Returns:
            List[UserContent]: The list of user contents matching the search criteria.

        Raises:
            Exception: If an error occurs while searching for user contents.
        """
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
        """
        Deletes a user content with the specified ID.

        Args:
            content_id (int): The ID of the user content to delete.

        Returns:
            dict: A dictionary with a message indicating the success of the deletion.

        Raises:
            Exception: If an error occurs while deleting the user content.
        """
        UserContentService.logger.info(f"Deleting content with ID: {content_id}")
        try:
            response = await HttpUtils.delete(
                f"{Config.USER_CONTENT_SERVICE_ENDPOINT}{content_id}",
            )
            return {"message": "Content deleted successfully"}
        except Exception as e:
            raise e
