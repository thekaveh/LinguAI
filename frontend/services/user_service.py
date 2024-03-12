import asyncio
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor

from schema.user import User
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.authentication import AuthenticationRequest, AuthenticationResponse
from schema.user import User, UserCreate


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
        
    @log_decorator
    def get_user_by_username_sync(username):
        
        def _fetch_user_by_username_sync(username):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(UserService.get_user_by_username(username))
            loop.close()
            
            return result
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_fetch_user_by_username_sync, username)
            
            return future.result()


    @log_decorator
    @staticmethod
    async def authenticate(request: AuthenticationRequest) -> AuthenticationResponse:
        try:
            return await HttpUtils.apost(
                Config.USER_SERVICE_AUTHENTICATE_ENDPOINT,
                request,
                response_model=AuthenticationResponse,
            )
        except Exception as e:
            raise e
        
    @log_decorator    
    @staticmethod   
    async def create_user(request: UserCreate) -> User:
        try:
            return await HttpUtils.apost(
                Config.USER_SERVICE_CREATE_ENDPOINT,
                request,
                response_model=User,
            )
        except Exception as e:
            raise e