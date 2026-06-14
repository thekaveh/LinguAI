from __future__ import annotations
import pytest
from unittest.mock import AsyncMock

import httpx

from viewmodels.auth.register_vm import build_register_vm
from viewmodels.shell.notification_center_vm import build_notification_center


@pytest.fixture
def lab(services):  # type: ignore[no-untyped-def]
    hub, dispatcher = services
    http = httpx.AsyncClient(base_url="http://test")
    notifications = build_notification_center(hub, dispatcher)
    vm, nx, bk, sub = build_register_vm(hub, dispatcher, http, notifications)
    return vm, nx, bk, sub


def test_next_disabled_until_account_valid(lab):  # type: ignore[no-untyped-def]
    vm, nx, *_ = lab
    assert not nx.can_execute()
    vm.account.set_username("alice")
    vm.account.set_email("a@b.c")
    vm.account.set_password("secret1")
    vm.account.set_confirm("secret1")
    assert nx.can_execute()
    nx.execute()
    assert vm.model.current_step == 1


def test_back_disabled_at_first_step(lab):  # type: ignore[no-untyped-def]
    vm, _, bk, _ = lab
    assert not bk.can_execute()


def test_submit_disabled_until_all_steps_valid(lab):  # type: ignore[no-untyped-def]
    vm, _, _, sub = lab
    assert not sub.can_execute()
    # Make all steps valid
    vm.account.set_username("alice")
    vm.account.set_email("a@b.c")
    vm.account.set_password("secret1")
    vm.account.set_confirm("secret1")
    vm.profile.set_first_name("Alice")
    vm.languages.set_native("English")
    vm.languages.set_learning(("Spanish",))
    # Move to step 2 (languages)
    vm.model = vm.model.__class__(current_step=2)
    assert sub.can_execute()


def test_password_plaintext_never_emitted_to_hub(lab, services):  # type: ignore[no-untyped-def]
    """Security regression test — typing a password must never put the
    plaintext on the hub's PropertyChangedMessage stream."""
    vm, *_ = lab
    hub, _ = services

    seen_messages = []
    hub.messages.subscribe(seen_messages.append)

    # Pre-clear messages from prior subscription/init traffic.
    seen_messages.clear()

    vm.account.set_password("hunter2-super-secret")
    vm.account.set_confirm("hunter2-super-secret")

    # The plaintext password must not appear in any message's str representation.
    for msg in seen_messages:
        as_str = repr(msg)
        assert "hunter2" not in as_str, (
            f"plaintext password leaked into hub message: {as_str!r}"
        )

    # …but the VM's model must reflect that a password is set.
    assert vm.account.model.has_password
    assert vm.account.model.has_confirm
    assert vm.account.model.passwords_match
    assert vm.account.model.password_long_enough
    # And the trusted accessor returns the actual value.
    assert vm.account.password() == "hunter2-super-secret"
