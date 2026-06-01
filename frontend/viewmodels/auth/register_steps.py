from __future__ import annotations
from dataclasses import dataclass, replace

from vmx import ComponentVMOf, MessageHub, RxDispatcher


@dataclass(frozen=True)
class AccountStep:
    """Account-creation step.

    Password and confirm-password are stored as `has_*: bool` flags on this
    immutable model so that the plaintext never lands in a `PropertyChangedMessage`
    emitted to the hub. The plaintext lives in private attributes on
    `AccountStepVM` (`_password`, `_confirm`), accessed only by trusted
    consumers (see `register_vm._to_user_create`).
    """

    username: str = ""
    email: str = ""
    has_password: bool = False
    has_confirm: bool = False
    passwords_match: bool = False
    password_long_enough: bool = False

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.username)
            and "@" in self.email
            and self.has_password
            and self.has_confirm
            and self.passwords_match
            and self.password_long_enough
        )


@dataclass(frozen=True)
class ProfileStep:
    preferred_name: str = ""
    first_name: str = ""
    last_name: str = ""

    @property
    def is_valid(self) -> bool:
        return bool(self.first_name)


@dataclass(frozen=True)
class LanguagesStep:
    native: str = ""
    learning: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return bool(self.native) and len(self.learning) >= 1


class AccountStepVM(ComponentVMOf[AccountStep]):
    """Note: plaintext password is stored on `self._password` / `self._confirm`,
    NOT on `self.model`. Reading the model gives only the validity flags.
    """

    _password: str
    _confirm: str

    def _bind_passwords(self) -> None:
        """Initialize the private password storage. Called once by the factory."""
        self._password = ""
        self._confirm = ""

    def set_username(self, v: str) -> None:
        self.model = replace(self.model, username=v)

    def set_email(self, v: str) -> None:
        self.model = replace(self.model, email=v)

    def set_password(self, v: str) -> None:
        self._password = v
        self.model = replace(
            self.model,
            has_password=bool(v),
            password_long_enough=len(v) >= 6,
            passwords_match=(v == self._confirm),
        )

    def set_confirm(self, v: str) -> None:
        self._confirm = v
        self.model = replace(
            self.model,
            has_confirm=bool(v),
            passwords_match=(self._password == v),
        )

    def password(self) -> str:
        """Trusted accessor — used by RegisterVM's submit path AND by the view
        when re-rendering the field after step navigation (so the user doesn't
        have to re-type their password when going Account → Profile → Back)."""
        return self._password

    def confirm(self) -> str:
        """Trusted accessor — same rationale as `password()`."""
        return self._confirm


class ProfileStepVM(ComponentVMOf[ProfileStep]):
    def set_preferred_name(self, v: str) -> None: self.model = replace(self.model, preferred_name=v)
    def set_first_name(self, v: str)     -> None: self.model = replace(self.model, first_name=v)
    def set_last_name(self, v: str)      -> None: self.model = replace(self.model, last_name=v)


class LanguagesStepVM(ComponentVMOf[LanguagesStep]):
    def set_native(self, v: str) -> None: self.model = replace(self.model, native=v)
    def set_learning(self, langs: tuple[str, ...]) -> None: self.model = replace(self.model, learning=langs)


def build_account_step(hub: MessageHub, dispatcher: RxDispatcher) -> AccountStepVM:
    vm = AccountStepVM(
        name="register-account", hint="",
        initial_model=AccountStep(),
        modeled_hinter=lambda m: "register-account",
        on_model_changed=None,
        hub=hub, dispatcher=dispatcher,
    )
    vm.construct()
    vm._bind_passwords()
    return vm


def build_profile_step(hub: MessageHub, dispatcher: RxDispatcher) -> ProfileStepVM:
    vm = ProfileStepVM(
        name="register-profile", hint="",
        initial_model=ProfileStep(),
        modeled_hinter=lambda m: "register-profile",
        on_model_changed=None,
        hub=hub, dispatcher=dispatcher,
    )
    vm.construct()
    return vm


def build_languages_step(hub: MessageHub, dispatcher: RxDispatcher) -> LanguagesStepVM:
    vm = LanguagesStepVM(
        name="register-languages", hint="",
        initial_model=LanguagesStep(),
        modeled_hinter=lambda m: "register-languages",
        on_model_changed=None,
        hub=hub, dispatcher=dispatcher,
    )
    vm.construct()
    return vm
