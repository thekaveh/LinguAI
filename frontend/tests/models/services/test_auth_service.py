import httpx
import pytest
import respx

from models.services.auth_service import AuthService
from models.schemas.authentication import AuthenticationRequest


@pytest.mark.asyncio
async def test_authenticate_success() -> None:
    async with httpx.AsyncClient(base_url="http://test/v1") as http:
        with respx.mock() as router:
            router.post("http://test/v1/users/authenticate").mock(
                return_value=httpx.Response(
                    200,
                    json={"status": True, "username": "alice", "message": "Login successful"},
                )
            )
            svc = AuthService(http)
            r = await svc.authenticate(AuthenticationRequest(username="alice", password="x"))
            assert r.ok is True
            assert r.username == "alice"
            assert r.token == "alice"  # username used as stand-in token


@pytest.mark.asyncio
async def test_authenticate_failure_status() -> None:
    async with httpx.AsyncClient(base_url="http://test/v1") as http:
        with respx.mock() as router:
            router.post("http://test/v1/users/authenticate").mock(
                return_value=httpx.Response(
                    200,
                    json={"status": False, "message": "Invalid credentials"},
                )
            )
            svc = AuthService(http)
            r = await svc.authenticate(AuthenticationRequest(username="alice", password="wrong"))
            assert r.ok is False
            assert r.token is None


@pytest.mark.asyncio
async def test_authenticate_http_error() -> None:
    async with httpx.AsyncClient(base_url="http://test/v1") as http:
        with respx.mock() as router:
            router.post("http://test/v1/users/authenticate").mock(return_value=httpx.Response(500))
            svc = AuthService(http)
            r = await svc.authenticate(AuthenticationRequest(username="alice", password="x"))
            assert r.ok is False
            assert "500" in r.message
