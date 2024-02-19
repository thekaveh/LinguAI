import asyncio
import streamlit as st

from services.llm_service import LLMService
from services.state_service import StateService
from services.persona_service import PersonaService

def render():
    st.title("Settings")
    
    state_service = StateService.instance()

    with st.expander("Chat", expanded=True):
        st.markdown("<hr>", unsafe_allow_html=True)
        
        models = asyncio.run(LLMService.list())
        personas = asyncio.run(PersonaService.list())
        
        new_model = st.selectbox(
			label="Model:"
			, options=models
			, key="chat.model"
			, index=models.index(state_service.model)
		)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        new_temperature = st.slider(
            step=0.1
            , min_value=0.0
            , max_value=1.0
            , label="Temperature:"
            , key="chat.temperature"
            , value=state_service.temperature
        )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        new_persona = st.selectbox(
			label="Persona:"
			, options=personas
			, key="chat.persona"
			, index=personas.index(state_service.persona)
		)
        
        state_service.model = new_model
        state_service.persona = new_persona
        state_service.temperature = new_temperature
