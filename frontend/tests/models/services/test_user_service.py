from __future__ import annotations
import httpx
import pytest
import respx

from models.services.user_service import UserService

_USER_ALICE = {
    "user_id": 1, "username": "alice", "email": "a@b.c",
    "user_type": "user", "first_name": "A", "last_name": "B",
}
_USER_BOB = {
    "user_id": 2, "username": "bob", "email": "b@b.c",
    "user_type": "admin", "first_name": "B", "last_name": "B",
}


@pytest.mark.asyncio
async def test_get_id_by_username() -> None:
    async with httpx.AsyncClient(base_url="http://test/v1") as http:
        with respx.mock() as router:
            router.get("http://test/v1/users/username/alice/id").mock(
                return_value=httpx.Response(200, json=42)
            )
            svc = UserService(http)
            assert await svc.get_id_by_username("alice") == 42


@pytest.mark.asyncio
async def test_list_users() -> None:
    async with httpx.AsyncClient(base_url="http://test/v1") as http:
        with respx.mock() as router:
            router.get("http://test/v1/users/list").mock(
                return_value=httpx.Response(200, json=[_USER_ALICE, _USER_BOB])
            )
            svc = UserService(http)
            users = await svc.list()
            assert len(users) == 2
            assert users[0].username == "alice"
            assert users[1].user_type == "admin"


@pytest.mark.asyncio
async def test_delete_by_username() -> None:
    async with httpx.AsyncClient(base_url="http://test/v1") as http:
        with respx.mock() as router:
            route = router.delete("http://test/v1/users/alice/delete").mock(
                return_value=httpx.Response(200)
            )
            svc = UserService(http)
            await svc.delete_by_username("alice")
            assert route.called
