from __future__ import annotations
import asyncio
from dataclasses import dataclass, replace

import httpx

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM


@dataclass(frozen=True)
class ChangePasswordForm:
    """Validity-flag booleans only — plaintext passwords are NEVER stored on the model."""

    has_current: bool = False
    has_new: bool = False
    has_confirm: bool = False
    new_long_enough: bool = False
    new_matches_confirm: bool = False
    error: str = ""
    in_flight: bool = False

    @property
    def is_ready(self) -> bool:
        return (
            self.has_current
            and self.has_new
            and self.has_confirm
            and self.new_long_enough
            and self.new_matches_confirm
            and not self.in_flight
        )


class ChangePasswordVM(ComponentVMOf[ChangePasswordForm]):
    """Plaintext passwords live in private attrs; model carries only validity flags."""

    # Private plaintext stores — set via setters only.
    _current: str
    _new: str
    _confirm: str

    def _bind_passwords(self) -> None:
        self._current = ""
        self._new = ""
        self._confirm = ""

    def set_current(self, v: str) -> None:
        self._current = v
        self.model = replace(self.model, has_current=bool(v))

    def set_new(self, v: str) -> None:
        self._new = v
        self.model = replace(
            self.model,
            has_new=bool(v),
            new_long_enough=len(v) >= 6,
            new_matches_confirm=(v == self._confirm),
        )

    def set_confirm(self, v: str) -> None:
        self._confirm = v
        self.model = replace(
            self.model,
            has_confirm=bool(v),
            new_matches_confirm=(self._new == v),
        )

    # Trusted read-only accessors (used only by the command body).
    def current(self) -> str:
        return self._current

    def new(self) -> str:
        return self._new

    def confirm(self) -> str:
        return self._confirm


def build_change_password_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    http: httpx.AsyncClient,
    session: UserSessionVM,
    notifications: NotificationCenterVM,
) -> tuple[ChangePasswordVM, RelayCommand]:
    """Build the ChangePasswordVM and its submit RelayCommand."""
    vm = ChangePasswordVM(
        name="change-password",
        hint="",
        initial_model=ChangePasswordForm(),
        modeled_hinter=lambda m: "change-password",
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    vm._bind_passwords()

    async def _do_submit() -> None:
        username = session.model.username
        if not username:
            vm.model = replace(vm.model, error="Not signed in.", in_flight=False)
            return
        try:
            r = await http.post(
                f"/users/{username}/change-password",
                json={"current_password": vm.current(), "new_password": vm.new()},
            )
            if r.status_code == 400:
                vm.model = replace(vm.model, in_flight=False, error="Current password incorrect.")
                return
            r.raise_for_status()
            notifications.push_success("Password changed.")
            # Reset fields.
            vm._current = ""
            vm._new = ""
            vm._confirm = ""
            vm.model = ChangePasswordForm()
        except httpx.HTTPError as e:
            vm.model = replace(vm.model, in_flight=False, error=f"Change failed: {e}")

    def _start() -> None:
        vm.model = replace(vm.model, in_flight=True, error="")
        asyncio.create_task(_do_submit())

    submit_cmd = (
        RelayCommand.builder()
        .task(_start)
        .predicate(lambda: vm.model.is_ready)
        .triggers(vm.property_changed)
        .build()
    )

    return vm, submit_cmd
