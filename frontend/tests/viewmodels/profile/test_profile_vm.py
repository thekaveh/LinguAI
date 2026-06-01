from __future__ import annotations
import pytest
from unittest.mock import AsyncMock
from dataclasses import replace
import httpx

from viewmodels.shell.user_session_vm import build_user_session_vm
from viewmodels.shell.notification_center_vm import build_notification_center
from viewmodels.profile.profile_vm import build_profile_vm


@pytest.fixture
def vm(services):  # type: ignore[no-untyped-def]
    hub, dispatcher = services
    auth = AsyncMock()
    http = httpx.AsyncClient(base_url="http://test")
    session = build_user_session_vm(hub, dispatcher, auth, http)
    notif = build_notification_center(hub, dispatcher)
    return build_profile_vm(
        hub, dispatcher, AsyncMock(), AsyncMock(), session, notif, http=http
    )


def test_save_disabled_until_first_name_set(vm) -> None:  # type: ignore[no-untyped-def]
    assert not vm.save_command.can_execute()
    vm.state.set_model(replace(vm.state.model, user_id=1, first_name="Alice"))
    assert vm.save_command.can_execute()


def test_route_is_profile(vm) -> None:  # type: ignore[no-untyped-def]
    assert vm.route == "profile"
