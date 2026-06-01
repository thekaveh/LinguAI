from __future__ import annotations
import asyncio
from dataclasses import dataclass, replace
from typing import Optional, Tuple

from vmx import ComponentVMOf, MessageHub, RxDispatcher

from viewmodels.app_shell_vm import PageVM
from viewmodels.shell.user_session_vm import UserSessionVM
from models.services.user_service import UserService


@dataclass(frozen=True)
class SkillCard:
    language: str
    code_iso: str       # "ES", "FR", "JA"
    level: str          # "B2 · Intermediate"
    percent_to_next: int
    delta_label: str    # "↑ 4%", "+12 xp", "new"


@dataclass(frozen=True)
class HomeModel:
    languages_in_progress: int = 0
    last_session_label: str = "(none yet)"
    skill_cards: Tuple[SkillCard, ...] = ()
    has_assessments: bool = False


# Multiple inheritance: HomeVM is a PageVM (for the AppShell router) AND a
# ComponentVMOf[HomeModel] (for the model).  Both bases share _ComponentVMBase
# so MRO is clean; ComponentVMOf supplies __init__ / model machinery.
class HomeVM(ComponentVMOf[HomeModel], PageVM):  # type: ignore[misc]
    route = "home"

    def _bind_user_svc(self, session: UserSessionVM, user_svc: UserService) -> None:
        """Wire the user service for assessment-count checking. Called by factory."""
        self._session: UserSessionVM = session
        self._user_svc: UserService = user_svc
        session.property_changed.subscribe(self._on_session_changed)

    def _on_session_changed(self, name: str) -> None:
        if name != "model":
            return
        if self._session.model.is_authenticated:
            try:
                asyncio.create_task(self._reload())
            except RuntimeError:
                pass  # no running loop — skip

    async def _reload(self) -> None:
        try:
            user = await self._user_svc.get_by_username(
                self._session.model.username or ""
            )
            assessments = getattr(user, "user_assessments", None) or []
            learning = getattr(user, "learning_languages", None) or []
            self.model = replace(
                self.model,
                has_assessments=bool(assessments),
                languages_in_progress=len(list(learning)),
            )
        except Exception:
            pass


def build_home_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    session: UserSessionVM,
    user_svc: Optional[UserService] = None,
) -> HomeVM:
    vm = HomeVM(
        name="home", hint="",
        initial_model=HomeModel(),
        modeled_hinter=lambda m: f"{m.languages_in_progress} languages",
        on_model_changed=None,
        hub=hub, dispatcher=dispatcher,
    )
    vm.construct()
    if user_svc is not None:
        vm._bind_user_svc(session, user_svc)
    return vm
