from typing import List

from core.config import Config
from models.schema.user import User
from utils.http_utils import HttpUtils

class UserService:
    @staticmethod
    async def list() -> List[User]:
        try:
            print("Config.USER_SERVICE_LIST_ENDPOINT :",Config.USER_SERVICE_LIST_ENDPOINT)
            return await HttpUtils.get(Config.USER_SERVICE_LIST_ENDPOINT, response_model=list[User])
        except Exception as e:
            raise e