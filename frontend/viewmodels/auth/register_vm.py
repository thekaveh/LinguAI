from __future__ import annotations
import asyncio
from dataclasses import dataclass, replace
from typing import Callable, Optional

import httpx

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.auth.register_steps import (
    ProfileStep, LanguagesStep,
    AccountStepVM, ProfileStepVM, LanguagesStepVM,
    build_account_step, build_profile_step, build_languages_step,
)
from viewmodels.shell.notification_center_vm import NotificationCenterVM

from models.schemas.user import UserCreate


@dataclass(frozen=True)
class RegisterState:
    current_step: int = 0   # 0=account, 1=profile, 2=languages
    in_flight: bool = False
    error: str = ""
    done: bool = False


class RegisterVM(ComponentVMOf[RegisterState]):
    """Wizard orchestrator. Holds three step VMs + own RegisterState."""

    account: AccountStepVM
    profile: ProfileStepVM
    languages: LanguagesStepVM

    def _bind(
        self,
        account: AccountStepVM,
        profile: ProfileStepVM,
        languages: LanguagesStepVM,
    ) -> None:
        self.account = account
        self.profile = profile
        self.languages = languages

    def next_step(self) -> None:
        if self.model.current_step < 2:
            self.model = replace(self.model, current_step=self.model.current_step + 1)

    def back_step(self) -> None:
        if self.model.current_step > 0:
            self.model = replace(self.model, current_step=self.model.current_step - 1)

    def current_step_valid(self) -> bool:
        steps = (
            self.account.model.is_valid,
            self.profile.model.is_valid,
            self.languages.model.is_valid,
        )
        return steps[self.model.current_step]

    def all_steps_valid(self) -> bool:
        return (
            self.account.model.is_valid
            and self.profile.model.is_valid
            and self.languages.model.is_valid
        )


def _to_user_create(
    account_vm: AccountStepVM,
    profile: ProfileStep,
    languages: LanguagesStep,
) -> UserCreate:
    """Build the UserCreate payload from the three step models.

    Note: backend field `password_hash` accepts plain password and hashes server-side.
    The plaintext password is pulled from `AccountStepVM.password()` rather than
    the model (the model only carries validity flags — see register_steps.py).
    """
    account = account_vm.model
    return UserCreate(
        username=account.username,
        email=account.email,
        password_hash=account_vm.password(),   # plain password from private VM attr; backend hashes
        user_type="user",
        first_name=profile.first_name,
        last_name=profile.last_name or "",
        preferred_name=profile.preferred_name or None,
        base_language=languages.native,
        learning_languages=list(languages.learning),
    )


def build_register_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    http: httpx.AsyncClient,
    notifications: NotificationCenterVM,
    on_complete: Optional[Callable[[], None]] = None,
) -> tuple[RegisterVM, RelayCommand, RelayCommand, RelayCommand]:
    """Returns (vm, next_command, back_command, submit_command)."""

    vm = RegisterVM(
        name="register", hint="",
        initial_model=RegisterState(),
        modeled_hinter=lambda m: f"step {m.current_step + 1}/3",
        on_model_changed=None,
        hub=hub, dispatcher=dispatcher,
    )
    vm.construct()

    vm._bind(
        build_account_step(hub, dispatcher),
        build_profile_step(hub, dispatcher),
        build_languages_step(hub, dispatcher),
    )

    next_cmd = (
        RelayCommand.builder()
        .task(vm.next_step)
        .predicate(lambda: vm.model.current_step < 2 and vm.current_step_valid())
        .triggers(vm.property_changed)
        .triggers(vm.account.property_changed)
        .triggers(vm.profile.property_changed)
        .triggers(vm.languages.property_changed)
        .build()
    )

    back_cmd = (
        RelayCommand.builder()
        .task(vm.back_step)
        .predicate(lambda: vm.model.current_step > 0)
        .triggers(vm.property_changed)
        .build()
    )

    async def _do_submit() -> None:
        try:
            payload = _to_user_create(vm.account, vm.profile.model, vm.languages.model)
            r = await http.post("/users/", json=payload.model_dump(mode="json"))
            r.raise_for_status()
            notifications.push_success("Account created. Please sign in.")
            vm.model = replace(vm.model, in_flight=False, done=True)
            if on_complete is not None:
                on_complete()
        except httpx.HTTPError as e:
            vm.model = replace(vm.model, in_flight=False, error=f"Registration failed: {e}")

    def _start_submit() -> None:
        vm.model = replace(vm.model, in_flight=True, error="")
        asyncio.create_task(_do_submit())

    submit_cmd = (
        RelayCommand.builder()
        .task(_start_submit)
        .predicate(
            lambda: vm.model.current_step == 2
            and vm.all_steps_valid()
            and not vm.model.in_flight
        )
        .triggers(vm.property_changed)
        .triggers(vm.account.property_changed)
        .triggers(vm.profile.property_changed)
        .triggers(vm.languages.property_changed)
        .build()
    )

    return vm, next_cmd, back_cmd, submit_cmd
