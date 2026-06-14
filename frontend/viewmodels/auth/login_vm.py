from __future__ import annotations
import asyncio
from dataclasses import dataclass, replace

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM


@dataclass(frozen=True)
class LoginForm:
    username: str = ""
    has_password: bool = False  # bool only — no plaintext on the model
    error: str = ""
    in_flight: bool = False


class LoginVM(ComponentVMOf[LoginForm]):
    """Construct via build_login_vm — never via .builder() (which returns base class)."""

    _password: str  # private — never published to the model / hub

    def set_username(self, value: str) -> None:
        self.model = replace(self.model, username=value)

    def set_password(self, value: str) -> None:
        self._password = value
        # Update only the has_password flag, never the plaintext.
        self.model = replace(self.model, has_password=bool(value))


def build_login_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    session: UserSessionVM,
    notifications: NotificationCenterVM,
) -> tuple[LoginVM, RelayCommand]:
    vm = LoginVM(
        name="login",
        hint="",
        initial_model=LoginForm(),
        modeled_hinter=lambda m: m.username,
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    vm._password = ""  # initialise private slot after construction

    async def _do_login() -> None:
        ok = await session.log_in(vm.model.username, vm._password)
        if ok:
            notifications.push_success(f"Welcome, {vm.model.username}")
            vm._password = ""
            vm.model = LoginForm()  # clear
        else:
            vm.model = replace(vm.model, in_flight=False, error="Login failed.")

    def _start() -> None:
        vm.model = replace(vm.model, in_flight=True, error="")
        asyncio.create_task(_do_login())

    cmd = (
        RelayCommand.builder()
        .task(_start)
        .predicate(lambda: bool(vm.model.username and vm.model.has_password and not vm.model.in_flight))
        .triggers(vm.property_changed)
        .build()
    )

    return vm, cmd
