from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal, Optional

import httpx

from vmx import ComponentVMOf, MessageHub, RxDispatcher

from core.http import set_bearer_token
from models.services.auth_service import AuthService
from models.schemas.authentication import AuthenticationRequest


BackendStatus = Literal["online", "offline", "unknown"]


@dataclass(frozen=True)
class UserSession:
    username: Optional[str] = None
    user_type: Optional[str] = None
    preferred_name: Optional[str] = None
    streak_days: int = 0
    token: Optional[str] = None
    backend_status: BackendStatus = "unknown"

    @property
    def is_authenticated(self) -> bool:
        return self.token is not None

    @property
    def is_admin(self) -> bool:
        return self.user_type == "admin"


class UserSessionVM(ComponentVMOf[UserSession]):
    """Per-client user session VM.

    Note: ComponentVMOf.builder() is a @staticmethod returning a base ComponentVMOf.
    This subclass is constructed directly via __init__ in the factory function.
    Dependencies (auth service, http client) are attached post-construction via
    _bind_deps().
    """

    def _bind_deps(self, auth_svc: AuthService, http: httpx.AsyncClient) -> None:
        """Attach the dependencies the factory builds with. Called once by the factory."""
        self._auth = auth_svc
        self._http = http

    async def log_in(self, username: str, password: str) -> bool:
        result = await self._auth.authenticate(
            AuthenticationRequest(username=username, password=password)
        )
        if result.ok and result.token:
            set_bearer_token(self._http, result.token)
            # Write partial session first so is_authenticated is True for follow-up calls.
            self.model = replace(
                self.model,
                username=result.username,
                user_type=result.user_type,
                token=result.token,
                backend_status="online",
            )
            # Enrich with user_type from backend (login response may omit it).
            try:
                from models.services.user_service import UserService  # noqa: PLC0415
                user_svc = UserService(self._http)
                user = await user_svc.get_by_username(result.username or "")
                self.model = replace(
                    self.model,
                    user_type=getattr(user, "user_type", None),
                    preferred_name=getattr(user, "preferred_name", None) or None,
                    streak_days=int(getattr(user, "consecutive_login_days", 0) or 0),
                )
            except Exception:
                pass  # backend down or schema diff; non-fatal — admin link just won't show
            return True
        return False

    async def log_out(self) -> None:
        await self._auth.logout()
        set_bearer_token(self._http, None)
        self.model = UserSession()

    def rehydrate(self, token: Optional[str], username: Optional[str]) -> None:
        """Called once on app startup if app.storage.user holds a saved token."""
        if token:
            set_bearer_token(self._http, token)
            self.model = replace(self.model, token=token, username=username)
            # Schedule async enrich to populate preferred_name + user_type from backend.
            import asyncio  # noqa: PLC0415

            async def _enrich() -> None:
                try:
                    from models.services.user_service import UserService  # noqa: PLC0415
                    user_svc = UserService(self._http)
                    user = await user_svc.get_by_username(username or "")
                    self.model = replace(
                        self.model,
                        user_type=getattr(user, "user_type", None),
                        preferred_name=getattr(user, "preferred_name", None) or None,
                        streak_days=int(getattr(user, "consecutive_login_days", 0) or 0),
                    )
                except Exception:
                    pass

            try:
                asyncio.create_task(_enrich())
            except RuntimeError:
                pass  # no running loop yet — preferred_name stays None


def build_user_session_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    auth_svc: AuthService,
    http: httpx.AsyncClient,
) -> UserSessionVM:
    """Factory: build and construct a UserSessionVM."""
    vm = UserSessionVM(
        name="user-session",
        hint="",
        initial_model=UserSession(),
        modeled_hinter=lambda m: m.username or "",
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    vm._bind_deps(auth_svc, http)
    return vm
