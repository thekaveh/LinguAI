from __future__ import annotations
import pytest
import httpx
from unittest.mock import AsyncMock

from viewmodels.shell.user_session_vm import build_user_session_vm
from viewmodels.shell.notification_center_vm import build_notification_center
from viewmodels.profile.change_password_vm import build_change_password_vm


@pytest.fixture
def lab(services):  # type: ignore[no-untyped-def]
    hub, dispatcher = services
    http = httpx.AsyncClient(base_url="http://test/v1")
    auth = AsyncMock()
    session = build_user_session_vm(hub, dispatcher, auth, http)
    # Manually set username so it looks authenticated.
    from dataclasses import replace as dc_replace
    session.model = dc_replace(session.model, username="alice", token="t")
    notif = build_notification_center(hub, dispatcher)
    return build_change_password_vm(hub, dispatcher, http, session, notif)


def test_submit_disabled_until_all_fields_valid(lab) -> None:  # type: ignore[no-untyped-def]
    vm, cmd = lab
    assert not cmd.can_execute()
    vm.set_current("oldpass")
    vm.set_new("newpass123")
    vm.set_confirm("newpass123")
    assert cmd.can_execute()


def test_submit_disabled_if_new_too_short(lab) -> None:  # type: ignore[no-untyped-def]
    vm, cmd = lab
    vm.set_current("oldpass")
    vm.set_new("short")  # less than 6 chars
    vm.set_confirm("short")
    assert not cmd.can_execute()


def test_submit_disabled_if_mismatch(lab) -> None:  # type: ignore[no-untyped-def]
    vm, cmd = lab
    vm.set_current("oldpass")
    vm.set_new("newpass123")
    vm.set_confirm("DIFFERENT")
    assert not cmd.can_execute()


def test_plaintext_never_on_model(lab) -> None:  # type: ignore[no-untyped-def]
    vm, _ = lab
    vm.set_new("super-secret-123")
    assert "super-secret" not in repr(vm.model)
    assert vm.new() == "super-secret-123"  # trusted accessor works


def test_exactly_6_chars_passes_length_check(lab) -> None:  # type: ignore[no-untyped-def]
    vm, cmd = lab
    vm.set_current("oldpass")
    vm.set_new("abcdef")  # exactly 6
    vm.set_confirm("abcdef")
    assert cmd.can_execute()
