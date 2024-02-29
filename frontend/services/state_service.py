import asyncio
import streamlit as st

from services.llm_service import LLMService
from services.persona_service import PersonaService

from models.common.chat_message import ChatMessage


class StateService:
    def __init__(self):
        self._init_model()
        self._init_persona()

        st.session_state["images"] = []
        st.session_state["messages"] = []
        st.session_state["temperature"] = 0.0
        st.session_state["chat_messages"] = []
        st.session_state["file_upload_key"] = 0

    def _init_model(self):
        models = asyncio.run(LLMService.list_models())

        if models and len(models) > 0:
            st.session_state["model"] = models[0]
        else:
            st.session_state["model"] = None

    def _init_persona(self):
        personas = asyncio.run(PersonaService.list())

        if personas and len(personas) > 0:
            st.session_state["persona"] = personas[0]
        else:
            st.session_state["persona"] = None

    @property
    def model(self):
        return st.session_state.get("model", None)

    @model.setter
    def model(self, value):
        st.session_state["model"] = value

    @property
    def temperature(self):
        return st.session_state.get("temperature", 0.0)

    @temperature.setter
    def temperature(self, value):
        st.session_state["temperature"] = value

    @property
    def persona(self):
        return st.session_state.get("persona", None)

    @persona.setter
    def persona(self, value):
        st.session_state["persona"] = value

    @property
    def file_upload_key(self):
        return st.session_state["file_upload_key"]

    def increment_file_upload_key(self):
        st.session_state["file_upload_key"] += 1

    @property
    def chat_messages(self):
        return st.session_state["chat_messages"]

    def append_chat_message(self, chat_message: ChatMessage) -> None:
        st.session_state["chat_messages"].append(chat_message)

    @staticmethod
    def instance():
        if "state_service" not in st.session_state:
            st.session_state["state_service"] = StateService()

        return st.session_state["state_service"]
