from __future__ import annotations
import asyncio
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple

import httpx

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.profile.interest_vm import InterestVM, build_interest_vm
from viewmodels.profile.assessment_history_vm import (
    AssessmentHistoryVM,
    HistoryEntry,
    build_assessment_history_vm,
)
from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM

from models.services.user_service import UserService
from models.services.topic_service import TopicService
from models.services.language_service import LanguageService
from models.schemas.user_topic import UserTopicBase


@dataclass(frozen=True)
class ProfileModel:
    user_id: Optional[int] = None
    username: str = ""
    preferred_name: str = ""
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    email: str = ""
    base_language: str = ""
    learning_languages: Tuple[str, ...] = field(default_factory=tuple)
    available_languages: Tuple[str, ...] = field(default_factory=tuple)
    gender: str = ""
    mobile_phone: str = ""
    contact_preference: str = ""
    in_flight: bool = False
    error: str = ""


class ProfileStateVM(ComponentVMOf[ProfileModel]):
    def set_model(self, m: ProfileModel) -> None:
        self.model = m


class ProfileVM:
    route = "profile"

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        user_svc: UserService,
        topic_svc: TopicService,
        lang_svc: LanguageService,
        session: UserSessionVM,
        notifications: NotificationCenterVM,
        history: AssessmentHistoryVM,
        http: httpx.AsyncClient,
    ) -> None:
        self._hub = hub
        self._dispatcher = dispatcher
        self._user_svc = user_svc
        self._topic_svc = topic_svc
        self._lang_svc = lang_svc
        self._session = session
        self._notify = notifications
        self.history = history
        self._http = http

        self.state = ProfileStateVM(
            name="profile-state",
            hint="",
            initial_model=ProfileModel(),
            modeled_hinter=lambda m: m.username or "(no user)",
            on_model_changed=None,
            hub=hub,
            dispatcher=dispatcher,
        )
        self.state.construct()

        self.interests: list[InterestVM] = []

        # Commands
        self.load_command = self._build_load_command()
        self.save_command = self._build_save_command()

        # Build change-password sub-VM
        from viewmodels.profile.change_password_vm import build_change_password_vm  # noqa: PLC0415
        self.change_password_vm, self.change_password_command = build_change_password_vm(
            hub, dispatcher, http, session, notifications,
        )

        # Auto-load when session reports an authenticated user.
        session.property_changed.subscribe(self._on_session_changed)

    # ---- session sync ----

    def _on_session_changed(self, name: str) -> None:
        if name != "model":
            return
        if self._session.model.is_authenticated and self.state.model.user_id is None:
            self.load_command.execute()

    # ---- field setters (called from view) ----

    def set_preferred_name(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, preferred_name=v))

    def set_first_name(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, first_name=v))

    def set_last_name(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, last_name=v))

    def set_middle_name(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, middle_name=v))

    def set_email(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, email=v))

    def set_gender(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, gender=v))

    def set_mobile_phone(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, mobile_phone=v))

    def set_contact_preference(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, contact_preference=v))

    def set_base_language(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, base_language=v))

    def set_learning_languages(self, langs: Tuple[str, ...]) -> None:
        self.state.set_model(replace(self.state.model, learning_languages=langs))

    # ---- command bodies ----

    async def _do_load(self) -> None:
        username = self._session.model.username
        if not username:
            return
        try:
            user = await self._user_svc.get_by_username(username)
            all_topics = await self._topic_svc.list()

            try:
                languages = await self._lang_svc.list()
                available_lang_names: Tuple[str, ...] = tuple(
                    L.language_name for L in languages
                )
            except Exception:
                available_lang_names = ()

            self.state.set_model(
                ProfileModel(
                    user_id=getattr(user, "user_id", None),
                    username=user.username,
                    preferred_name=getattr(user, "preferred_name", None) or "",
                    first_name=user.first_name or "",
                    last_name=user.last_name or "",
                    middle_name=getattr(user, "middle_name", None) or "",
                    email=str(user.email) if user.email else "",
                    base_language=getattr(user, "base_language", None) or "",
                    learning_languages=tuple(
                        getattr(user, "learning_languages", None) or ()
                    ),
                    available_languages=available_lang_names,
                    gender=getattr(user, "gender", None) or "",
                    mobile_phone=getattr(user, "mobile_phone", None) or "",
                    contact_preference=getattr(user, "contact_preference", None) or "",
                )
            )

            user_topic_names = {
                t.topic_name
                for t in (getattr(user, "user_topics", None) or [])
            }
            self.interests = [
                build_interest_vm(
                    self._hub,
                    self._dispatcher,
                    t.topic_name,
                    selected=(t.topic_name in user_topic_names),
                )
                for t in all_topics
            ]

            history_entries: list[HistoryEntry] = []
            for a in getattr(user, "user_assessments", None) or []:
                lang = (
                    getattr(a, "language_name", "")
                    or getattr(getattr(a, "language", None), "language_name", "")
                    or ""
                )
                level = getattr(a, "skill_level", "") or ""
                date_str = str(getattr(a, "assessment_date", ""))[:10]
                history_entries.append(
                    HistoryEntry(language=lang, skill_level=level, date_iso=date_str)
                )
            self.history.set_entries(history_entries)
            if history_entries:
                self.history.set_language_filter(history_entries[0].language)
        except Exception as e:
            self._notify.push_error(f"Could not load profile: {e}")

    async def _do_save(self) -> None:
        m = self.state.model
        if not m.username:
            return
        self.state.set_model(replace(m, in_flight=True, error=""))
        try:
            user = await self._user_svc.get_by_username(m.username)
            updated = user.model_copy(
                update={
                    "preferred_name": m.preferred_name or None,
                    "first_name": m.first_name,
                    "last_name": m.last_name,
                    "middle_name": m.middle_name or None,
                    "email": m.email,
                    "base_language": m.base_language or None,
                    "gender": m.gender or None,
                    "mobile_phone": m.mobile_phone or None,
                    "contact_preference": m.contact_preference or None,
                    "learning_languages": list(m.learning_languages) if m.learning_languages else None,
                }
            )
            await self._user_svc.update(m.username, updated)
            # learning_languages is handled by a separate backend endpoint;
            # /update ignores it, so persist it explicitly or it's silently lost.
            await self._user_svc.update_languages(m.username, updated)

            uid = m.user_id or 0
            selected_topics = [
                UserTopicBase(user_id=uid, topic_name=c.model.topic_name)
                for c in self.interests
                if c.model.selected
            ]
            await self._user_svc.set_topics(m.username, selected_topics)

            self._notify.push_success("Profile saved.")
            self.state.set_model(replace(self.state.model, in_flight=False))
        except Exception as e:
            self.state.set_model(
                replace(self.state.model, in_flight=False, error=f"Save failed: {e}")
            )

    # ---- command builders ----

    def _build_load_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_load())

        return RelayCommand.builder().task(_start).build()

    def _build_save_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_save())

        return (
            RelayCommand.builder()
            .task(_start)
            .predicate(
                lambda: bool(
                    self.state.model.first_name and not self.state.model.in_flight
                )
            )
            .triggers(self.state.property_changed)
            .build()
        )


def build_profile_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    user_svc: UserService,
    topic_svc: TopicService,
    session: UserSessionVM,
    notifications: NotificationCenterVM,
    lang_svc: Optional[LanguageService] = None,
    http: Optional[httpx.AsyncClient] = None,
) -> ProfileVM:
    # Provide a no-op http client if not given (test/backward-compat path).
    if http is None:
        http = httpx.AsyncClient(base_url="http://localhost")
    if lang_svc is None:
        lang_svc = LanguageService(http)
    return ProfileVM(
        hub,
        dispatcher,
        user_svc,
        topic_svc,
        lang_svc,
        session,
        notifications,
        build_assessment_history_vm(hub, dispatcher),
        http,
    )
