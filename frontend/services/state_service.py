import asyncio
import streamlit as st

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

        st.session_state["chat_messages"] = []
        st.session_state["chat_messages"] = []
        st.session_state["chat_file_upload_key"] = 0

        st.session_state["username"] = None
        st.session_state["session_user"] = None

        st.session_state["review_writing"] = ""
        st.session_state["rewrite_content"] = ""
        st.session_state["content_reading"] = ""

    @log_decorator
    def clear_session_state(self):
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            del st.session_state[key]

    @log_decorator
    def _init_model(self):
        models = asyncio.run(LLMService.list_models())

        if models and len(models) > 0:
            st.session_state["model"] = models[0]
        else:
            st.session_state["model"] = None

    @log_decorator
    def _init_persona(self):
        personas = asyncio.run(PersonaService.get_all())

        if personas:
            st.session_state["persona"] = next(
                (p.persona_name for p in personas if p.is_default), personas[0]
            )
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
        if value and value != self.model:
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
    def content_reading(self):
        return st.session_state["content_reading"]

    @content_reading.setter
    def content_reading(self, value):
        st.session_state["content_reading"] = value

    @log_decorator
    @staticmethod
    def instance():
        if "state_service" not in st.session_state:
            st.session_state["state_service"] = StateService()

        return st.session_state["state_service"]
