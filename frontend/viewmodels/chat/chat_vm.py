from __future__ import annotations
import asyncio
import base64
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Optional

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.chat.chat_message_vm import ChatMessageVM, ChatBubble, build_chat_message_vm
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.shell.settings_vm import SettingsVM

from models.domain.llm import LLM
from models.domain.persona import Persona
from models.schemas.chat import ChatRequest, ChatMessage
from models.services.chat_service import ChatService
from models.services.llm_service import LLMService
from models.services.persona_service import PersonaService
from models.services.text_to_speech_service import TextToSpeechService
from models.schemas.text_to_speech import TextToSpeechRequest


@dataclass(frozen=True)
class ChatSession:
    personas: tuple[Persona, ...] = ()
    llms: tuple[LLM, ...] = ()
    persona: Optional[Persona] = None
    llm: Optional[LLM] = None
    temperature: float = 0.7
    draft: str = ""
    attached_images_b64: tuple[str, ...] = ()
    tts_enabled: bool = False
    in_flight: bool = False
    last_audio_data_url: Optional[str] = None

    @property
    def is_vision_llm(self) -> bool:
        if self.llm is None:
            return False
        # LLM.vision is an int score; positive means the LLM supports vision.
        vision_score = getattr(self.llm, "vision", None)
        if isinstance(vision_score, int) and vision_score > 0:
            return True
        # Fallback: check string-typed attributes for "vision" keyword
        for attr in ("purpose", "endpoint_type", "capability", "capabilities"):
            val = getattr(self.llm, attr, None)
            if val is None:
                continue
            if isinstance(val, str) and "vision" in val.lower():
                return True
            if isinstance(val, (list, tuple)) and any("vision" in str(v).lower() for v in val):
                return True
        return False

    @property
    def can_attach(self) -> bool:
        return self.is_vision_llm and not self.in_flight

    @property
    def can_send(self) -> bool:
        return (
            self.persona is not None
            and self.llm is not None
            and bool(self.draft.strip())
            and not self.in_flight
        )


class ChatStateVM(ComponentVMOf[ChatSession]):
    def set_model(self, m: ChatSession) -> None:
        self.model = m


class ChatVM:
    route = "chat"

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        chat_svc: ChatService,
        llm_svc: LLMService,
        persona_svc: PersonaService,
        tts_svc: TextToSpeechService,
        settings: SettingsVM,
        notifications: NotificationCenterVM,
    ) -> None:
        self._hub = hub
        self._dispatcher = dispatcher
        self._chat = chat_svc
        self._llm = llm_svc
        self._persona = persona_svc
        self._tts = tts_svc
        self._settings = settings
        self._notify = notifications

        self.state = ChatStateVM(
            name="chat-state", hint="",
            initial_model=ChatSession(),
            modeled_hinter=lambda m: m.persona.persona_name if m.persona else "(no persona)",
            on_model_changed=None,
            hub=hub, dispatcher=dispatcher,
        )
        self.state.construct()

        self.messages: list[ChatMessageVM] = []

        self.load_options_command = self._build_load_options_command()
        self.send_command = self._build_send_command()
        self.clear_command = self._build_clear_command()

    # ---- field setters (called from view) ----

    def set_persona(self, persona: Persona) -> None:
        self.state.set_model(replace(self.state.model, persona=persona))

    def set_llm(self, llm: LLM) -> None:
        self.state.set_model(replace(self.state.model, llm=llm))

    def set_temperature(self, t: float) -> None:
        self.state.set_model(replace(self.state.model, temperature=t))

    def set_draft(self, text: str) -> None:
        self.state.set_model(replace(self.state.model, draft=text))

    def toggle_tts(self) -> None:
        self.state.set_model(replace(self.state.model, tts_enabled=not self.state.model.tts_enabled))

    MAX_ATTACHMENTS = 4

    def attach_image_bytes(self, data: bytes) -> None:
        if not self.state.model.is_vision_llm:
            self._notify.push_warning("Current LLM doesn't support vision; attachment ignored.")
            return
        existing = self.state.model.attached_images_b64
        if len(existing) >= self.MAX_ATTACHMENTS:
            self._notify.push_warning(
                f"Maximum {self.MAX_ATTACHMENTS} images per message; ignoring extra."
            )
            return
        encoded = base64.b64encode(data).decode("ascii")
        self.state.set_model(replace(
            self.state.model,
            attached_images_b64=existing + (encoded,),
        ))

    def clear_attachments(self) -> None:
        self.state.set_model(replace(self.state.model, attached_images_b64=()))

    def remove_attachment(self, index: int) -> None:
        existing = self.state.model.attached_images_b64
        if 0 <= index < len(existing):
            self.state.set_model(replace(
                self.state.model,
                attached_images_b64=existing[:index] + existing[index + 1:],
            ))

    # ---- command bodies ----

    async def _do_load_options(self) -> None:
        try:
            personas = await self._persona.list()
            llms = await self._llm.get_content()
            if not (personas and llms):
                self._notify.push_error("Could not load personas or LLMs.")
                return

            # Honor user's persisted defaults if available.
            default_persona = next((p for p in personas if getattr(p, "is_default", False)), personas[0])
            if self._settings.model.default_persona_id:
                default_persona = next(
                    (p for p in personas if getattr(p, "id", None) == self._settings.model.default_persona_id),
                    default_persona,
                )

            default_llm = llms[0]
            if self._settings.model.default_llm_id:
                default_llm = next(
                    (m for m in llms if getattr(m, "id", None) == self._settings.model.default_llm_id),
                    default_llm,
                )

            self.state.set_model(replace(
                self.state.model,
                personas=tuple(personas),
                llms=tuple(llms),
                persona=default_persona,
                llm=default_llm,
            ))
        except Exception as e:
            self._notify.push_error(f"Loading chat options failed: {e}")

    async def _do_send(self) -> None:
        s = self.state.model
        if not (s.persona and s.llm and s.draft.strip()):
            return

        now = datetime.now().isoformat(timespec="seconds")
        user_bubble = ChatBubble(
            role="user", text=s.draft, timestamp_iso=now,
            images_b64=s.attached_images_b64,
        )
        self.messages.append(build_chat_message_vm(self._hub, self._dispatcher, user_bubble))

        asst_bubble = ChatBubble(
            role="assistant", text="",
            timestamp_iso=datetime.now().isoformat(timespec="seconds"),
            is_streaming=True,
        )
        assistant_vm = build_chat_message_vm(self._hub, self._dispatcher, asst_bubble)
        self.messages.append(assistant_vm)

        # Nudge state so any subscribers re-render the message list.
        self.state.set_model(replace(s, in_flight=True, draft="", attached_images_b64=()))

        try:
            chat_messages = [
                ChatMessage(
                    sender=m.model.role,
                    text=m.model.text,
                    images=list(m.model.images_b64) if m.model.images_b64 else None,
                )
                for m in self.messages[:-1]  # exclude the in-flight assistant bubble
            ]
            req = ChatRequest(
                llm_id=int(getattr(s.llm, "id", 0)),
                messages=chat_messages,
                persona=getattr(s.persona, "persona_name", "Neutral"),
                temperature=s.temperature,
            )
            async for chunk in self._chat.stream(req):
                assistant_vm.append_text(chunk)
            assistant_vm.finalize()
            # Push the message list update one more time so the view repaints the final state.
            self.state.set_model(replace(self.state.model))

            if s.tts_enabled and assistant_vm.model.text.strip():
                # Best-effort TTS; don't block on failures.
                try:
                    result = await self._tts.synthesize(TextToSpeechRequest(
                        text=assistant_vm.model.text,
                        lang=getattr(s.persona, "language", None) or "en",
                    ))
                    data_url = f"data:audio/mp3;base64,{result.audio}"
                    self.state.set_model(replace(self.state.model, last_audio_data_url=data_url))
                    self._notify.push_info("Audio ready.")
                except Exception:
                    pass

        except Exception as e:
            self._notify.push_error(f"Chat send failed: {e}")
            assistant_vm.append_text(f"\n[error: {e}]")
            assistant_vm.finalize()
        finally:
            self.state.set_model(replace(self.state.model, in_flight=False))

    def _do_clear(self) -> None:
        self.messages = []
        # Force a model update to trigger re-render.
        self.state.set_model(replace(self.state.model))

    # ---- command builders ----

    def _build_load_options_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_load_options())
        return RelayCommand.builder().task(_start).build()

    def _build_send_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_send())
        return (
            RelayCommand.builder()
            .task(_start)
            .predicate(lambda: self.state.model.can_send)
            .triggers(self.state.property_changed)
            .build()
        )

    def _build_clear_command(self) -> RelayCommand:
        return RelayCommand.builder().task(self._do_clear).build()


def build_chat_vm(
    hub: MessageHub, dispatcher: RxDispatcher,
    chat_svc: ChatService, llm_svc: LLMService, persona_svc: PersonaService,
    tts_svc: TextToSpeechService, settings: SettingsVM, notifications: NotificationCenterVM,
) -> ChatVM:
    return ChatVM(hub, dispatcher, chat_svc, llm_svc, persona_svc, tts_svc, settings, notifications)
