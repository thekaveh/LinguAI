import asyncio
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock, MagicMock

import pytest

from schema.user import User
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.authentication import AuthenticationRequest, AuthenticationResponse
from schema.user import User, UserCreate
from services.user_service import UserService

@pytest.mark.asyncio
async def test_list_users():
    # Mocks
    expected_users = [User(user_id=3, username="blackwidow123", email="blackwidow@example.com", user_type="external", first_name="Natasha", last_name="Romanoff"), User(user_id=5, username="hulk123", email="hulk@example.com", user_type="external", first_name="Bruce", last_name="Banner")]
    HttpUtils.get = AsyncMock(return_value=expected_users)

    # Test
    users = await UserService.list()

    # Assertions
    assert all(user in users for user in expected_users)
    HttpUtils.get.assert_awaited_once_with(Config.USER_SERVICE_LIST_ENDPOINT, response_model=list[User])

@pytest.mark.asyncio
async def test_get_user_by_username():
    # Mocks
    expected_user = User(user_id=5, username="hulk123", email="hulk@example.com", user_type="external", first_name="Bruce", last_name="Banner")
    HttpUtils.get = AsyncMock(return_value=expected_user)

    # Test
    user = await UserService.get_user_by_username("hulk123")

    # Assertions
    assert user == expected_user
    HttpUtils.get.assert_awaited_once_with(Config.USER_SERVICE_USERNAME_ENDPOINT + "hulk123", response_model=User)

def test_get_user_by_username_sync():
    # Mocks
    expected_user = User(user_id=5, username="hulk123", email="hulk@example.com", user_type="external", first_name="Bruce", last_name="Banner")
    HttpUtils.get = AsyncMock(return_value=expected_user)
    async def fake_get_user_by_username(username):
        return expected_user
    UserService.get_user_by_username = MagicMock(wraps=fake_get_user_by_username)

    # Test
    user = UserService.get_user_by_username_sync("hulk123")

    # Assertions
    assert user == expected_user

@pytest.mark.asyncio
async def test_authenticate():
    # Mocks
    request = AuthenticationRequest(username="hulk123", password="password_hash_hulk")
    expected_response = AuthenticationResponse(status=True, message="Authentication successful", token="test_token")
    HttpUtils.apost = AsyncMock(return_value=expected_response)

    # Test
    response = await UserService.authenticate(request)

    # Assertions
    assert response == expected_response
    HttpUtils.apost.assert_awaited_once_with(Config.USER_SERVICE_AUTHENTICATE_ENDPOINT, request, response_model=AuthenticationResponse)

@pytest.mark.asyncio
async def test_create_user():
    # Mocks
    request = UserCreate(username="hulk123", password_hash="password_hash_hulk", email="hulk@example.com", user_type="external", first_name="Bruce", last_name="Banner")
    expected_user = User(user_id=5, username="hulk123", email="hulk@example.com", user_type="external", first_name="Bruce", last_name="Banner")
    HttpUtils.apost = AsyncMock(return_value=expected_user)

    # Test
    user = await UserService.create_user(request)

    # Assertions
    assert user == expected_user
    HttpUtils.apost.assert_awaited_once_with(Config.USER_SERVICE_CREATE_ENDPOINT, request, response_model=User)