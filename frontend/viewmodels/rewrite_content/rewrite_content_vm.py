from __future__ import annotations
import asyncio
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.content_history import ContentHistoryHelper
from models.services.rewrite_content_service import RewriteContentService
from models.services.language_service import LanguageService
from models.services.llm_service import LLMService
from models.services.text_to_speech_service import TextToSpeechService
from models.services.user_service import UserService
from models.services.user_content_service import UserContentService
from models.schemas.rewrite_content import ContentRewriteReq
from models.schemas.text_to_speech import TextToSpeechRequest
from models.schemas.user_content import UserContent

STYLE_OPTIONS = ["formal", "casual", "academic", "humorous", "concise"]


@dataclass(frozen=True)
class RewriteContentState:
    languages: Tuple[str, ...] = field(default_factory=tuple)
    llms: Tuple[object, ...] = field(default_factory=tuple)
    llm_id: int = 0
    language: str = "English"
    skill_level: str = "B1"
    user_skill_level: str = "B1"
    user_base_language: str = "English"
    target_style: str = "formal"
    source_text: str = ""
    temperature: float = 0.5
    result: str = ""
    in_flight: bool = False
    last_audio_data_url: Optional[str] = None
    history: Tuple[UserContent, ...] = field(default_factory=tuple)


class RewriteContentStateVM(ComponentVMOf[RewriteContentState]):
    def set_model(self, m: RewriteContentState) -> None:
        self.model = m


class RewriteContentVM:
    route = "rewrite_content"

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        svc: RewriteContentService,
        llm_svc: LLMService,
        tts_svc: TextToSpeechService,
        user_svc: UserService,
        session: UserSessionVM,
        notifications: NotificationCenterVM,
        lang_svc: Optional[LanguageService] = None,
        user_content_svc: Optional[UserContentService] = None,
    ) -> None:
        self._hub = hub
        self._dispatcher = dispatcher
        self._svc = svc
        self._llm = llm_svc
        self._tts = tts_svc
        self._user = user_svc
        self._lang = lang_svc
        self._session = session
        self._notify = notifications
        self._history: Optional[ContentHistoryHelper] = (
            ContentHistoryHelper(
                content_type=1,
                user_content_svc=user_content_svc,
                user_svc=user_svc,
                session=session,
                notifications=notifications,
            )
            if user_content_svc is not None
            else None
        )

        self.state = RewriteContentStateVM(
            name="rewrite-content-state",
            hint="",
            initial_model=RewriteContentState(),
            modeled_hinter=lambda m: m.target_style,
            on_model_changed=None,
            hub=hub,
            dispatcher=dispatcher,
        )
        self.state.construct()

        self.load_command = self._build_load_command()
        self.rewrite_command = self._build_rewrite_command()
        self.speak_command = self._build_speak_command()

    # ---- field setters ----

    def set_source_text(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, source_text=v))

    def set_target_style(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, target_style=v))

    def set_language(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, language=v))

    def set_skill_level(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, skill_level=v))

    def set_user_skill_level(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, user_skill_level=v))

    def set_user_base_language(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, user_base_language=v))

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
            llms = await self._llm.get_content()
            if not llms:
                self._notify.push_error("Could not load LLM options.")
                return

            # Load language list if service is available
            lang_names: Tuple[str, ...] = ()
            if self._lang is not None:
                try:
                    lang_objs = await self._lang.list()
                    lang_names = tuple(L.language_name for L in lang_objs)
                except Exception:
                    pass

            # Derive user language and skill level from profile
            default_lang = lang_names[0] if lang_names else "English"
            derived_level = "B1"
            base_lang = default_lang
            if self._session.model.username:
                try:
                    user = await self._user.get_by_username(self._session.model.username)
                    base_lang = getattr(user, "base_language", None) or default_lang
                    learning = list(getattr(user, "learning_languages", None) or [])
                    default_lang = learning[0] if learning else base_lang
                    # Match language name against loaded list
                    if lang_names and default_lang not in lang_names:
                        default_lang = lang_names[0]
                    # Derive skill level from assessments
                    for a in (getattr(user, "user_assessments", None) or []):
                        lang_obj = getattr(a, "language", None)
                        lang_name = (
                            getattr(lang_obj, "language_name", "") if lang_obj else ""
                        )
                        # Match against the intended default learning language
                        target = learning[0] if learning else base_lang
                        if lang_name == target:
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
                languages=lang_names,
                llms=tuple(llms),
                llm_id=int(getattr(llms[0], "id", 0)),
                language=default_lang,
                skill_level=derived_level,
                user_skill_level=derived_level,
                user_base_language=base_lang,
                history=history,
            ))
        except Exception as e:
            self._notify.push_error(f"Loading options failed: {e}")

    async def _do_rewrite(self) -> None:
        s = self.state.model
        if not (s.llm_id and s.source_text.strip()):
            return

        username = self._session.model.username or ""
        user_id = 0
        try:
            if username:
                user_id = await self._user.get_id_by_username(username)
        except Exception:
            pass

        req = ContentRewriteReq(
            user_id=user_id,
            language=s.language,
            skill_level=s.skill_level,
            input_content=s.source_text,
            llm_id=s.llm_id,
            temperature=s.temperature,
            user_skill_level=s.user_skill_level,
            user_base_language=s.user_base_language,
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
                    user_content=self.state.model.source_text or None,
                    gen_content=self.state.model.result,
                    language=self.state.model.language,
                    level=self.state.model.skill_level,
                )
                self.state.set_model(
                    replace(self.state.model, history=await self._history.fetch())
                )
        except Exception as e:
            self.state.set_model(replace(self.state.model, in_flight=False))
            self._notify.push_error(f"Rewrite failed: {e}")

    async def _do_speak(self) -> None:
        s = self.state.model
        if not s.result.strip():
            return
        try:
            result = await self._tts.synthesize(
                TextToSpeechRequest(text=s.result, lang="en")
            )
            # Backend already returns a full data: URI (data:audio/mpeg;base64,...)
            data_url = result.audio
            self.state.set_model(replace(self.state.model, last_audio_data_url=data_url))
            self._notify.push_info("Audio ready.")
        except Exception as e:
            self._notify.push_error(f"TTS failed: {e}")

    # ---- command builders ----

    def _build_load_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_load())
        return RelayCommand.builder().task(_start).build()

    def _build_rewrite_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_rewrite())
        return (
            RelayCommand.builder()
            .task(_start)
            .predicate(lambda: bool(
                self.state.model.llm_id
                and self.state.model.source_text.strip()
                and not self.state.model.in_flight
            ))
            .triggers(self.state.property_changed)
            .build()
        )

    def _build_speak_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_speak())
        return (
            RelayCommand.builder()
            .task(_start)
            .predicate(lambda: bool(self.state.model.result.strip()))
            .triggers(self.state.property_changed)
            .build()
        )


def build_rewrite_content_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    svc: RewriteContentService,
    llm_svc: LLMService,
    tts_svc: TextToSpeechService,
    user_svc: UserService,
    session: UserSessionVM,
    notifications: NotificationCenterVM,
    lang_svc: Optional[LanguageService] = None,
    user_content_svc: Optional[UserContentService] = None,
) -> RewriteContentVM:
    return RewriteContentVM(
        hub, dispatcher, svc, llm_svc, tts_svc, user_svc,
        session, notifications, lang_svc, user_content_svc,
    )
