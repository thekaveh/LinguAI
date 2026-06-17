from __future__ import annotations
import asyncio
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.content_history import ContentHistoryHelper
from models.services.review_writing_service import ReviewWritingService
from models.services.llm_service import LLMService
from models.services.language_service import LanguageService
from models.services.user_service import UserService
from models.services.user_content_service import UserContentService
from models.schemas.review_writing import ReviewWritingReq
from models.schemas.language import Language
from models.schemas.user_content import UserContent

SKILL_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

_NEXT_LEVEL: dict[str, str] = {
    "A1": "A2",
    "A2": "B1",
    "B1": "B2",
    "B2": "C1",
    "C1": "C2",
    "C2": "C2",
}


_ISO_TO_NAME: dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "zh-cn": "Mandarin",
    "zh-tw": "Mandarin",
    "ru": "Russian",
    "ar": "Arabic",
    "ko": "Korean",
}


@dataclass(frozen=True)
class ReviewWritingState:
    languages: Tuple[Language, ...] = field(default_factory=tuple)
    llms: Tuple[object, ...] = field(default_factory=tuple)
    language: str = "English"
    curr_skill_level: str = "B1"
    next_skill_level: str = "B2"
    strength: str = ""
    weakness: str = ""
    input_content: str = ""
    detected_language: Optional[str] = None
    llm_id: int = 0
    temperature: float = 0.5
    result: str = ""
    in_flight: bool = False
    history: Tuple[UserContent, ...] = field(default_factory=tuple)


class ReviewWritingStateVM(ComponentVMOf[ReviewWritingState]):
    def set_model(self, m: ReviewWritingState) -> None:
        self.model = m


class ReviewWritingVM:
    route = "review_writing"

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        svc: ReviewWritingService,
        llm_svc: LLMService,
        lang_svc: LanguageService,
        user_svc: UserService,
        session: UserSessionVM,
        notifications: NotificationCenterVM,
        user_content_svc: Optional[UserContentService] = None,
    ) -> None:
        self._hub = hub
        self._dispatcher = dispatcher
        self._svc = svc
        self._llm = llm_svc
        self._lang = lang_svc
        self._user = user_svc
        self._session = session
        self._notify = notifications
        self._history: Optional[ContentHistoryHelper] = (
            ContentHistoryHelper(
                content_type=2,
                user_content_svc=user_content_svc,
                user_svc=user_svc,
                session=session,
                notifications=notifications,
            )
            if user_content_svc is not None
            else None
        )

        self.state = ReviewWritingStateVM(
            name="review-writing-state",
            hint="",
            initial_model=ReviewWritingState(),
            modeled_hinter=lambda m: m.language,
            on_model_changed=None,
            hub=hub,
            dispatcher=dispatcher,
        )
        self.state.construct()

        self.load_command = self._build_load_command()
        self.review_command = self._build_review_command()

    # ---- field setters ----

    def set_input_content(self, v: str) -> None:
        detected: Optional[str] = None
        if v.strip():
            try:
                import langdetect  # type: ignore[import-untyped]  # noqa: PLC0415
                iso = langdetect.detect(v)
                detected = _ISO_TO_NAME.get(iso, iso)
            except Exception:
                detected = None
        self.state.set_model(replace(self.state.model, input_content=v, detected_language=detected))

    def set_language(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, language=v))

    def set_curr_skill_level(self, v: str) -> None:
        next_level = _NEXT_LEVEL.get(v, v)
        self.state.set_model(replace(
            self.state.model,
            curr_skill_level=v,
            next_skill_level=next_level,
        ))

    def set_next_skill_level(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, next_skill_level=v))

    def set_strength(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, strength=v))

    def set_weakness(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, weakness=v))

    def set_temperature(self, t: float) -> None:
        self.state.set_model(replace(self.state.model, temperature=t))

    def set_llm_id(self, llm_id: int) -> None:
        self.state.set_model(replace(self.state.model, llm_id=llm_id))

    def request_delete(self, content_id: int) -> None:
        async def _do() -> None:
            if self._history is not None:
                await self._history.delete(content_id)
                self.state.set_model(
                    replace(self.state.model, history=await self._history.fetch())
                )
        asyncio.create_task(_do())

    # ---- async work ----

    async def _do_load(self) -> None:
        try:
            languages = await self._lang.list()
            llms = await self._llm.get_content()
            if not llms:
                self._notify.push_error("Could not load LLM options.")
                return

            lang_name = languages[0].language_name if languages else "English"
            derived_level = "B1"

            if self._session.model.username:
                try:
                    user = await self._user.get_by_username(self._session.model.username)
                    base_lang = getattr(user, "base_language", None) or "English"
                    learning = list(getattr(user, "learning_languages", None) or [])
                    default_lang = learning[0] if learning else base_lang
                    # Validate against loaded languages
                    lang_names = [L.language_name for L in languages]
                    if default_lang in lang_names:
                        lang_name = default_lang
                    elif lang_names:
                        lang_name = lang_names[0]
                    # Derive skill level from assessments
                    target_lang = learning[0] if learning else base_lang
                    for a in (getattr(user, "user_assessments", None) or []):
                        lang_obj = getattr(a, "language", None)
                        aname = (
                            getattr(lang_obj, "language_name", "") if lang_obj else ""
                        )
                        if aname == target_lang:
                            derived_level = getattr(a, "skill_level", "B1") or "B1"
                            break
                except Exception:
                    pass

            # Load history
            history: Tuple[UserContent, ...] = ()
            if self._history is not None:
                history = await self._history.fetch()

            self.state.set_model(replace(
                self.state.model,
                languages=tuple(languages) if languages else (),
                llms=tuple(llms),
                language=lang_name,
                llm_id=int(getattr(llms[0], "id", 0)),
                curr_skill_level=derived_level,
                next_skill_level=_NEXT_LEVEL.get(derived_level, "B2"),
                history=history,
            ))
        except Exception as e:
            self._notify.push_error(f"Loading options failed: {e}")

    async def _do_review(self) -> None:
        s = self.state.model
        if not (s.llm_id and s.input_content.strip()):
            return

        username = self._session.model.username or ""
        user_id = 0
        try:
            if username:
                user_id = await self._user.get_id_by_username(username)
        except Exception:
            pass

        req = ReviewWritingReq(
            user_id=user_id,
            language=s.language,
            curr_skill_level=s.curr_skill_level,
            next_skill_level=s.next_skill_level,
            strength=s.strength,
            weakness=s.weakness,
            input_content=s.input_content,
            llm_id=s.llm_id,
            temperature=s.temperature,
        )

        self.state.set_model(replace(s, in_flight=True, result=""))
        try:
            buffer: list[str] = []
            async for chunk in self._svc.stream(req):
                buffer.append(chunk)
                self.state.set_model(replace(self.state.model, result="".join(buffer)))
            self.state.set_model(replace(self.state.model, in_flight=False))
            # Save to history
            if self._history is not None:
                await self._history.save(
                    user_content=self.state.model.input_content or None,
                    gen_content=self.state.model.result,
                    language=self.state.model.language,
                    level=self.state.model.curr_skill_level,
                )
                self.state.set_model(
                    replace(self.state.model, history=await self._history.fetch())
                )
        except Exception as e:
            self.state.set_model(replace(self.state.model, in_flight=False))
            self._notify.push_error(f"Review failed: {e}")

    # ---- command builders ----

    def _build_load_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_load())
        return RelayCommand.builder().task(_start).build()

    def _build_review_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_review())
        return (
            RelayCommand.builder()
            .task(_start)
            .predicate(lambda: bool(
                self.state.model.llm_id
                and self.state.model.input_content.strip()
                and not self.state.model.in_flight
            ))
            .triggers(self.state.property_changed)
            .build()
        )


def build_review_writing_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    svc: ReviewWritingService,
    llm_svc: LLMService,
    lang_svc: LanguageService,
    user_svc: UserService,
    session: UserSessionVM,
    notifications: NotificationCenterVM,
    user_content_svc: Optional[UserContentService] = None,
) -> ReviewWritingVM:
    return ReviewWritingVM(
        hub, dispatcher, svc, llm_svc, lang_svc, user_svc,
        session, notifications, user_content_svc,
    )
