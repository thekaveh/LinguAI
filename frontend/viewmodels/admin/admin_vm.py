from __future__ import annotations
import asyncio
from dataclasses import dataclass, replace
from typing import Optional, Tuple

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from models.services.ping_service import PingService
from models.services.user_service import UserService
from models.schemas.user import User


@dataclass(frozen=True)
class AdminState:
    users: Tuple[User, ...] = ()
    last_ping: str = "(no ping yet)"
    pending_delete_username: Optional[str] = None   # set when delete confirm dialog is open
    in_flight: bool = False


class AdminStateVM(ComponentVMOf[AdminState]):
    def set_model(self, m: AdminState) -> None:
        self.model = m


class AdminVM:
    """Admin page VM — list users, delete users, ping backend."""

    route = "admin"

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        ping_svc: PingService,
        user_svc: UserService,
        session: UserSessionVM,
        notifications: NotificationCenterVM,
    ) -> None:
        self._hub = hub
        self._dispatcher = dispatcher
        self._ping = ping_svc
        self._user_svc = user_svc
        self._session = session
        self._notify = notifications

        self.state = AdminStateVM(
            name="admin-state", hint="",
            initial_model=AdminState(),
            modeled_hinter=lambda m: f"{len(m.users)} users",
            on_model_changed=None,
            hub=hub, dispatcher=dispatcher,
        )
        self.state.construct()

        self.load_users_command = self._build_load_users_command()
        self.refresh_command = self.load_users_command  # alias
        self.ping_command = self._build_ping_command()
        self.confirm_delete_command = self._build_confirm_delete_command()
        self.cancel_delete_command = self._build_cancel_delete_command()
        self.execute_delete_command = self._build_execute_delete_command()

    def request_delete(self, username: str) -> None:
        """Called from the view when admin clicks a delete button. Opens the confirm dialog."""
        if username == (self._session.model.username or ""):
            self._notify.push_warning("You cannot delete your own account from here.")
            return
        self.state.set_model(replace(self.state.model, pending_delete_username=username))

    async def _do_load_users(self) -> None:
        try:
            users = await self._user_svc.list()
            self.state.set_model(replace(self.state.model, users=tuple(users)))
        except Exception as e:
            self._notify.push_error(f"Could not load users: {e}")

    async def _do_ping(self) -> None:
        r = await self._ping.ping()
        self.state.set_model(replace(self.state.model, last_ping=r.message))
        if r.ok:
            self._notify.push_success(f"Backend OK: {r.message}")
        else:
            self._notify.push_error(f"Backend ping failed: {r.message}")

    async def _do_execute_delete(self) -> None:
        username = self.state.model.pending_delete_username
        if not username:
            return
        self.state.set_model(replace(self.state.model, in_flight=True))
        try:
            await self._user_svc.delete_by_username(username)
            self._notify.push_success(f"Deleted user: {username}")
            # Reload list
            users = await self._user_svc.list()
            self.state.set_model(replace(
                self.state.model, users=tuple(users),
                pending_delete_username=None, in_flight=False,
            ))
        except Exception as e:
            self.state.set_model(replace(
                self.state.model, in_flight=False, pending_delete_username=None,
            ))
            self._notify.push_error(f"Delete failed: {e}")

    def _cancel_delete(self) -> None:
        self.state.set_model(replace(self.state.model, pending_delete_username=None))

    # ---- command builders ----

    def _build_load_users_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_load_users())
        return RelayCommand.builder().task(_start).build()

    def _build_ping_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_ping())
        return RelayCommand.builder().task(_start).build()

    def _build_confirm_delete_command(self) -> RelayCommand:
        """No-op — the view calls request_delete(username) directly because it needs the username."""
        return RelayCommand.builder().task(lambda: None).build()

    def _build_cancel_delete_command(self) -> RelayCommand:
        return RelayCommand.builder().task(self._cancel_delete).build()

    def _build_execute_delete_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_execute_delete())
        return RelayCommand.builder() \
            .task(_start) \
            .predicate(lambda: self.state.model.pending_delete_username is not None and not self.state.model.in_flight) \
            .triggers(self.state.property_changed) \
            .build()


def build_admin_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    ping_svc: PingService,
    user_svc: UserService,
    session: UserSessionVM,
    notifications: NotificationCenterVM,
) -> AdminVM:
    return AdminVM(hub, dispatcher, ping_svc, user_svc, session, notifications)
