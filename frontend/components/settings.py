import asyncio
from utils.logger import log_decorator
import streamlit as st

from services.llm_service import LLMService
from services.state_service import StateService
from services.persona_service import PersonaService


@log_decorator
def render():
    st.title("Settings")

    state_service = StateService.instance()

    with st.expander("Chat", expanded=True):
        st.markdown("<hr>", unsafe_allow_html=True)

        models = asyncio.run(LLMService.list_models())
        personas = asyncio.run(PersonaService.list())

        new_model = st.selectbox(
            label="Model:",
            key="chat.model",
            disabled=not models,
            options=models if models else ["No models available"],
            index=models.index(state_service.model) if models else 0,
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        new_temperature = st.slider(
            step=0.1,
            min_value=0.0,
            max_value=1.0,
            label="Temperature:",
            key="chat.temperature",
            value=state_service.temperature,
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        new_persona = st.selectbox(
            label="Persona:",
            key="chat.persona",
            disabled=not personas,
            options=personas if personas else ["No personas available"],
            index=personas.index(state_service.persona) if personas else 0,
        )

        state_service.model = (
            new_model if new_model is not "No models available" else None
        )
        state_service.persona = (
            new_persona if new_persona is not "No personas available" else None
        )
        state_service.temperature = new_temperature
