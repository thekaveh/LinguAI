from __future__ import annotations
import asyncio
import pytest
from unittest.mock import AsyncMock
from dataclasses import replace

import httpx

from viewmodels.admin.admin_vm import build_admin_vm
from viewmodels.shell.user_session_vm import build_user_session_vm
from viewmodels.shell.notification_center_vm import build_notification_center
from models.services.auth_service import AuthService


@pytest.fixture
def vm(services):  # type: ignore[no-untyped-def]
    hub, dispatcher = services
    http = httpx.AsyncClient(base_url="http://test/v1")
    auth = AuthService(http)
    session = build_user_session_vm(hub, dispatcher, auth, http)
    notif = build_notification_center(hub, dispatcher)
    ping = AsyncMock()
    user = AsyncMock()
    return build_admin_vm(hub, dispatcher, ping, user, session, notif), session


def test_request_delete_opens_dialog(vm) -> None:  # type: ignore[no-untyped-def]
    v, _ = vm
    v.request_delete("alice")
    assert v.state.model.pending_delete_username == "alice"


def test_request_delete_self_blocks(vm) -> None:  # type: ignore[no-untyped-def]
    v, session = vm
    # Set session username so 'kaveh' is "self"
    session.model = replace(session.model, username="kaveh")
    v.request_delete("kaveh")
    assert v.state.model.pending_delete_username is None  # didn't set


def test_cancel_delete_clears(vm) -> None:  # type: ignore[no-untyped-def]
    v, _ = vm
    v.request_delete("alice")
    v.cancel_delete_command.execute()
    assert v.state.model.pending_delete_username is None


def test_execute_delete_disabled_when_nothing_pending(vm) -> None:  # type: ignore[no-untyped-def]
    v, _ = vm
    assert not v.execute_delete_command.can_execute()
    v.request_delete("alice")
    assert v.execute_delete_command.can_execute()


@pytest.mark.asyncio
async def test_execute_delete_calls_service(vm) -> None:  # type: ignore[no-untyped-def]
    v, _ = vm
    v._user_svc.delete_by_username = AsyncMock(return_value=None)
    v._user_svc.list = AsyncMock(return_value=[])
    v.request_delete("alice")
    v.execute_delete_command.execute()
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    v._user_svc.delete_by_username.assert_called_once_with("alice")
    # After success, pending should be cleared
    assert v.state.model.pending_delete_username is None
