import asyncio
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
        self._init_model()
        self._init_persona()

        st.session_state["temperature"] = 0.0

        self._chat_tts = False
        self._chat_temperature = 0.0
        st.session_state["chat_messages"] = []
        self._chat_llm = LLMService.get_chat()[0]
        st.session_state["chat_file_upload_key"] = 0

        self._content_tts = False
        self._content_temperature = 0.0
        self._content_llm = LLMService.get_content()[0]

        st.session_state["username"] = None
        st.session_state["session_user"] = None

        st.session_state["review_writing"] = ""
        st.session_state["rewrite_content"] = ""
        st.session_state["content_reading"] = ""

        st.session_state["vision_llm"] = LLMService.get_vision()[0]
        st.session_state["embeddings_llm"] = LLMService.get_embeddings()[0]

    @log_decorator
    def clear_session_state(self):
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            del st.session_state[key]

    @log_decorator
    def _init_model(self):
        models = LLMService.get_all()

        if models:
            st.session_state["model"] = next(
                (m.name for m in models if m.content > 0), None
            )
        else:
            st.session_state["model"] = None

    @log_decorator
    def _init_persona(self):
        personas = PersonaService.get_all()

        if personas:
            default_persona = next((p for p in personas if p.is_default), personas[0])

            self._chat_persona = default_persona
            st.session_state["persona"] = default_persona.persona_name

        else:
            st.session_state["persona"] = None

    @property
    def session_user(self):
        return st.session_state.get("session_user", None)

    @session_user.setter
    def session_user(self, value):
        st.session_state["session_user"] = value

    @property
    def username(self):
        return st.session_state.get("username", None)

    @username.setter
    def username(self, value):
        st.session_state["username"] = value

    @property
    def model(self):
        return st.session_state.get("model", None)

    @model.setter
    def model(self, value):
        if value and (
            (not st.session_state["model"]) or (value != st.session_state["model"])
        ):
            st.session_state["model"] = value

            NotificationService.success(f"LLM Model setting changed to {value}")

    @property
    def temperature(self):
        return st.session_state.get("temperature", 0.0)

    @temperature.setter
    def temperature(self, value):
        if value != self.temperature:
            st.session_state["temperature"] = value

            NotificationService.success(f"LLM Temperature setting changed to {value}")

    @property
    def persona(self):
        return st.session_state.get("persona", None)

    @persona.setter
    def persona(self, value):
        if value and value != self.temperature:
            st.session_state["persona"] = value

            NotificationService.success(f"Persona setting changed to {value}")

    @property
    def chat_file_upload_key(self):
        return st.session_state["chat_file_upload_key"]

    def chat_increment_file_upload_key(self):
        st.session_state["chat_file_upload_key"] += 1

    @property
    def chat_messages(self):
        return st.session_state["chat_messages"]

    def chat_append_message(self, chat_message: ChatMessage) -> None:
        st.session_state["chat_messages"].append(chat_message)

    def chat_clear_messages(self):
        st.session_state["chat_messages"] = []

    @property
    def rewrite_content(self):
        return st.session_state["rewrite_content"]

    @rewrite_content.setter
    def rewrite_content(self, value):
        st.session_state["rewrite_content"] = value

    @property
    def review_writing(self):
        return st.session_state["review_writing"]

    @review_writing.setter
    def review_writing(self, value):
        st.session_state["review_writing"] = value

    @property
    def user_type(self):
        return st.session_state.get("user_type", None)

    @user_type.setter
    def user_type(self, value):
        st.session_state["user_type"] = value

    @property
    def content_reading(self):
        return st.session_state["content_reading"]

    @content_reading.setter
    def content_reading(self, value):
        st.session_state["content_reading"] = value

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
        return st.session_state["vision_llm"]

    @vision_llm.setter
    def vision_llm(self, value: LLM) -> None:
        st.session_state["vision_llm"] = value

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
        return st.session_state["embeddings_llm"]

    @embeddings_llm.setter
    def embeddings_llm(self, value: LLM) -> None:
        st.session_state["embeddings_llm"] = value

    @log_decorator
    @staticmethod
    def instance():
        if "state_service" not in st.session_state:
            st.session_state["state_service"] = StateService()

        return st.session_state["state_service"]
