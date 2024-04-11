import streamlit as st

from models.llm import LLM
from models.persona import Persona
from schema.chat import ChatMessage
from utils.logger import log_decorator
from services.llm_service import LLMService
from services.persona_service import PersonaService
from services.notification_service import NotificationService


class StateService:
    @log_decorator
    def __init__(self):
        self.reset_fields()

    @log_decorator
    def reset_fields(self):
        self._init_persona()

        self._chat_tts = False
        self._chat_messages = []
        self._chat_temperature = 0.0
        self._chat_file_upload_key = 0
        self._chat_llm = LLMService.get_chat()[0]

        self._content_tts = False
        self._content_temperature = 0.0
        self._content_llm = LLMService.get_content()[0]

        self._username = None
        self._user_type = None
        self._session_user = None

        self._review_writing = ""
        self._rewrite_content = ""
        self._content_reading = ""

        self._vision_llm = LLMService.get_vision()[0]
        self._embeddings_llm = LLMService.get_embeddings()[0]

    @log_decorator
    def _init_persona(self):
        personas = PersonaService.get_all()

        if personas:
            default_persona = next((p for p in personas if p.is_default), personas[0])

            self._chat_persona = default_persona
        else:
            self._chat_persona = None

    @property
    def session_user(self):
        return self._session_user

    @session_user.setter
    def session_user(self, value):
        self._session_user = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def chat_file_upload_key(self):
        return self._chat_file_upload_key

    def chat_increment_file_upload_key(self):
        self._chat_file_upload_key += 1

    @property
    def chat_messages(self):
        return self._chat_messages

    def chat_append_message(self, chat_message: ChatMessage) -> None:
        self._chat_messages.append(chat_message)

    def chat_clear_messages(self):
        self._chat_messages = []

    @property
    def rewrite_content(self):
        return self._rewrite_content

    @rewrite_content.setter
    def rewrite_content(self, value):
        self._rewrite_content = value

    @property
    def review_writing(self):
        return self._review_writing

    @review_writing.setter
    def review_writing(self, value):
        self._review_writing = value

    @property
    def user_type(self):
        return self._user_type

    @user_type.setter
    def user_type(self, value):
        self._user_type = value

    @property
    def content_reading(self):
        return self._content_reading

    @content_reading.setter
    def content_reading(self, value):
        self._content_reading = value

    @property
    def chat_llm(self) -> LLM:
        return self._chat_llm

    @chat_llm.setter
    def chat_llm(self, value: LLM) -> None:
        if value != self._chat_llm:
            self._chat_llm = value

            NotificationService.success(f"Chat LLM changed to {value.display_name()}")

    @property
    def chat_temperature(self) -> float:
        return self._chat_temperature

    @chat_temperature.setter
    def chat_temperature(self, value: float) -> None:
        if value != self._chat_temperature:
            self._chat_temperature = value

            NotificationService.success(f"Chat Temperature changed to {value}")

    @property
    def chat_persona(self) -> Persona:
        return self._chat_persona

    @chat_persona.setter
    def chat_persona(self, value: Persona) -> None:
        if value != self._chat_persona:
            self._chat_persona = value

            NotificationService.success(f"Chat Persona changed to {value.persona_name}")

    @property
    def chat_tts(self) -> bool:
        return self._chat_tts

    @chat_tts.setter
    def chat_tts(self, value: bool) -> None:
        if value != self._chat_tts:
            self._chat_tts = value

            NotificationService.success(f"Chat TTS changed to {value}")

    @property
    def vision_llm(self) -> LLM:
        return self._vision_llm

    @vision_llm.setter
    def vision_llm(self, value: LLM) -> None:
        self._vision_llm = value

    @property
    def content_llm(self) -> LLM:
        return self._content_llm

    @content_llm.setter
    def content_llm(self, value: LLM) -> None:
        if value != self._content_llm:
            self._content_llm = value

            NotificationService.success(
                f"Content LLM changed to {value.display_name()}"
            )

    @property
    def content_temperature(self) -> float:
        return self._content_temperature

    @content_temperature.setter
    def content_temperature(self, value: float) -> None:
        if value != self._content_temperature:
            self._content_temperature = value

            NotificationService.success(f"Content Temperature changed to {value}")

    @property
    def content_tts(self) -> bool:
        return self._content_tts

    @content_tts.setter
    def content_tts(self, value: bool) -> None:
        if value != self._content_tts:
            self._content_tts = value

            NotificationService.success(f"Content TTS changed to {value}")

    @property
    def embeddings_llm(self) -> LLM:
        return self._embeddings_llm

    @embeddings_llm.setter
    def embeddings_llm(self, value: LLM) -> None:
        self._embeddings_llm = value

    @log_decorator
    @staticmethod
    def instance():
        if "state_service" not in st.session_state:
            st.session_state["state_service"] = StateService()

        return st.session_state["state_service"]
