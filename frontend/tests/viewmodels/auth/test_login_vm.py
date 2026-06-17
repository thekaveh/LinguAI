from __future__ import annotations
import asyncio
import pytest
import respx
import httpx
from unittest.mock import AsyncMock

from viewmodels.shell.user_session_vm import build_user_session_vm
from viewmodels.shell.notification_center_vm import build_notification_center
from viewmodels.auth.login_vm import build_login_vm
from models.services.auth_service import AuthResult


@pytest.fixture
def lab(services):
    hub, dispatcher = services
    auth = AsyncMock()
    auth.authenticate = AsyncMock(return_value=AuthResult(
        ok=True, username="alice", token="alice", message="Login successful"
    ))
    http = httpx.AsyncClient(base_url="http://test/v1")
    session = build_user_session_vm(hub, dispatcher, auth, http)
    notifications = build_notification_center(hub, dispatcher)
    vm, cmd = build_login_vm(hub, dispatcher, session, notifications)
    return vm, cmd, session, notifications, auth, http


def test_command_disabled_when_fields_empty(lab):
    vm, cmd, *_ = lab
    assert not cmd.can_execute()


def test_command_enabled_when_fields_present(lab):
    vm, cmd, *_ = lab
    vm.set_username("alice")
    vm.set_password("x")
    assert cmd.can_execute()


@pytest.mark.asyncio
async def test_login_success_clears_form_and_notifies(lab):
    vm, cmd, session, notifications, _, _http = lab
    vm.set_username("alice")
    vm.set_password("x")
    # Mock the follow-up get_by_username that log_in calls to enrich user_type.
    with respx.mock() as router:
        router.get("http://test/v1/users/username/alice").mock(
            return_value=httpx.Response(
                200,
                json={
                    "user_id": 1,
                    "username": "alice",
                    "email": "alice@test.com",
                    "user_type": "user",
                    "first_name": "Alice",
                    "last_name": "Test",
                },
            )
        )
        cmd.execute()
        for _ in range(4):
            await asyncio.sleep(0)
    assert vm.model.username == ""  # cleared on success
    assert session.model.is_authenticated
    assert notifications.count == 1


@pytest.mark.asyncio
async def test_login_failure_surfaces_error(lab):
    vm, cmd, session, notifications, auth, _ = lab
    auth.authenticate = AsyncMock(return_value=AuthResult(ok=False, message="bad"))
    vm.set_username("alice")
    vm.set_password("x")
    cmd.execute()
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert vm.model.error == "Login failed."
    assert not session.model.is_authenticated
