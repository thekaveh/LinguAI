from __future__ import annotations
import asyncio
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.content_history import ContentHistoryHelper
from models.services.content_gen_service import ContentGenService
from models.services.language_service import LanguageService
from models.services.llm_service import LLMService
from models.services.user_service import UserService
from models.services.user_content_service import UserContentService
from models.services.topic_service import TopicService
from models.services.text_to_speech_service import TextToSpeechService
from models.schemas.content_gen import ContentGenReq
from models.schemas.text_to_speech import TextToSpeechRequest
from models.schemas.content import Content
from models.schemas.language import Language
from models.schemas.user_content import UserContent


@dataclass(frozen=True)
class ContentGenState:
    languages: Tuple[Language, ...] = field(default_factory=tuple)
    llms: Tuple[object, ...] = field(default_factory=tuple)
    language: Optional[Language] = None
    llm_id: int = 0
    skill_level: str = "B1"
    temperature: float = 0.5
    topic: str = ""
    result: str = ""
    in_flight: bool = False
    last_audio_data_url: Optional[str] = None
    suggested_topics: Tuple[str, ...] = field(default_factory=tuple)
    history: Tuple[UserContent, ...] = field(default_factory=tuple)


class ContentGenStateVM(ComponentVMOf[ContentGenState]):
    def set_model(self, m: ContentGenState) -> None:
        self.model = m


class ContentGenVM:
    route = "content_gen"

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        svc: ContentGenService,
        llm_svc: LLMService,
        lang_svc: LanguageService,
        user_svc: UserService,
        tts_svc: TextToSpeechService,
        session: UserSessionVM,
        notifications: NotificationCenterVM,
        user_content_svc: Optional[UserContentService] = None,
        topic_svc: Optional[TopicService] = None,
    ) -> None:
        self._hub = hub
        self._dispatcher = dispatcher
        self._svc = svc
        self._llm = llm_svc
        self._lang = lang_svc
        self._user = user_svc
        self._tts = tts_svc
        self._topic_svc = topic_svc
        self._session = session
        self._notify = notifications
        self._history: Optional[ContentHistoryHelper] = (
            ContentHistoryHelper(
                content_type=3,
                user_content_svc=user_content_svc,
                user_svc=user_svc,
                session=session,
                notifications=notifications,
            )
            if user_content_svc is not None
            else None
        )

        self.state = ContentGenStateVM(
            name="content-gen-state",
            hint="",
            initial_model=ContentGenState(),
            modeled_hinter=lambda m: m.topic,
            on_model_changed=None,
            hub=hub,
            dispatcher=dispatcher,
        )
        self.state.construct()

        self.load_command = self._build_load_command()
        self.generate_command = self._build_generate_command()
        self.speak_command = self._build_speak_command()

    # ---- field setters ----

    def set_topic(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, topic=v))

    def set_skill_level(self, v: str) -> None:
        self.state.set_model(replace(self.state.model, skill_level=v))

    def set_temperature(self, t: float) -> None:
        self.state.set_model(replace(self.state.model, temperature=t))

    def set_language(self, lang: Language) -> None:
        self.state.set_model(replace(self.state.model, language=lang))

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
            if not (languages and llms):
                self._notify.push_error("Could not load options.")
                return

            # Derive user skill level and preferred language
            default_language: Optional[Language] = languages[0] if languages else None
            derived_level = "B1"
            if self._session.model.username:
                try:
                    user = await self._user.get_by_username(self._session.model.username)
                    learning = list(getattr(user, "learning_languages", None) or [])
                    default_lang_name = learning[0] if learning else (
                        getattr(user, "base_language", None) or "English"
                    )
                    # Find the matching Language object
                    matched = next(
                        (L for L in languages if L.language_name == default_lang_name),
                        None,
                    )
                    if matched is not None:
                        default_language = matched
                    # Derive skill level from assessments
                    for a in (getattr(user, "user_assessments", None) or []):
                        lang_obj = getattr(a, "language", None)
                        lang_name = (
                            getattr(lang_obj, "language_name", "") if lang_obj else ""
                        )
                        if lang_name == default_lang_name:
                            derived_level = getattr(a, "skill_level", "B1") or "B1"
                            break
                except Exception:
                    pass

            # Gather suggested topics from user profile
            suggested: Tuple[str, ...] = ()
            if self._session.model.username:
                try:
                    user2 = await self._user.get_by_username(self._session.model.username)
                    user_topics = getattr(user2, "user_topics", None) or []
                    suggested = tuple(
                        t.topic_name
                        for t in user_topics
                        if getattr(t, "topic_name", None)
                    )
                    if not suggested and self._topic_svc is not None:
                        all_topics = await self._topic_svc.list()
                        suggested = tuple(
                            t.topic_name
                            for t in all_topics
                            if getattr(t, "topic_name", None)
                        )
                except Exception:
                    pass

            # Load history
            history: Tuple[UserContent, ...] = ()
            if self._history is not None:
                history = await self._history.fetch()

            self.state.set_model(replace(
                self.state.model,
                languages=tuple(languages),
                llms=tuple(llms),
                language=default_language,
                llm_id=int(getattr(llms[0], "id", 0)),
                skill_level=derived_level,
                suggested_topics=suggested,
                history=history,
            ))
        except Exception as e:
            self._notify.push_error(f"Loading options failed: {e}")

    async def _do_generate(self) -> None:
        s = self.state.model
        if not (s.language and s.llm_id and s.topic.strip()):
            return

        username = self._session.model.username or ""
        user_id = 0
        try:
            if username:
                user_id = await self._user.get_id_by_username(username)
        except Exception:
            pass

        # Content schema: content_name (str, required) + content_id (int, required).
        # We use the topic as the name and 0 as a placeholder id.
        content_payload = Content(content_name=s.topic, content_id=0)

        req = ContentGenReq(
            user_id=user_id,
            user_topics=[s.topic],
            content=content_payload,
            language=s.language,
            skill_level=s.skill_level,
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
                lang_name: Optional[str] = (
                    getattr(self.state.model.language, "language_name", None)
                    if self.state.model.language is not None
                    else None
                )
                await self._history.save(
                    user_content=self.state.model.topic or None,
                    gen_content=self.state.model.result,
                    language=lang_name,
                    level=self.state.model.skill_level,
                )
                self.state.set_model(
                    replace(self.state.model, history=await self._history.fetch())
                )
        except Exception as e:
            self.state.set_model(replace(self.state.model, in_flight=False))
            self._notify.push_error(f"Generation failed: {e}")

    async def _do_speak(self) -> None:
        s = self.state.model
        if not s.result.strip():
            return
        try:
            lang_code = "en"
            if s.language is not None:
                lang_code = getattr(s.language, "language_code", None) or "en"
            result = await self._tts.synthesize(TextToSpeechRequest(text=s.result, lang=lang_code))
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

    def _build_generate_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_generate())
        return (
            RelayCommand.builder()
            .task(_start)
            .predicate(lambda: bool(
                self.state.model.language
                and self.state.model.llm_id
                and self.state.model.topic.strip()
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


def build_content_gen_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    svc: ContentGenService,
    llm_svc: LLMService,
    lang_svc: LanguageService,
    user_svc: UserService,
    tts_svc: TextToSpeechService,
    session: UserSessionVM,
    notifications: NotificationCenterVM,
    user_content_svc: Optional[UserContentService] = None,
    topic_svc: Optional[TopicService] = None,
) -> ContentGenVM:
    return ContentGenVM(
        hub, dispatcher, svc, llm_svc, lang_svc, user_svc, tts_svc,
        session, notifications, user_content_svc, topic_svc,
    )
