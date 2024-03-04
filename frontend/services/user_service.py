from typing import List, Optional

from schema.user import User
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils


class UserService:
    @log_decorator
    @staticmethod
    async def list() -> List[User]:
        try:
            print(
                "Config.USER_SERVICE_LIST_ENDPOINT :", Config.USER_SERVICE_LIST_ENDPOINT
            )
            return await HttpUtils.get(
                Config.USER_SERVICE_LIST_ENDPOINT, response_model=list[User]
            )
        except Exception as e:
            raise e

    @log_decorator
    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        try:
            # Assuming Config.BASE_URL contains the base URL of your backend service
            # and you need to append '/users/username/{username}' to it
            user_service_endpoint = f"{Config.USER_SERVICE_USERNAME_ENDPOINT}{username}"
            print("user_service_endpoint :", user_service_endpoint)
            return await HttpUtils.get(user_service_endpoint, response_model=User)
        except Exception as e:
            raise e
