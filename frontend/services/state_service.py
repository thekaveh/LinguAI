import asyncio
import streamlit as st

from services.llm_service import LLMService
from services.persona_service import PersonaService

class StateService:
    def __init__(self):
        st.session_state['model'] = asyncio.run(LLMService.list())[0]
        st.session_state['temperature'] = 0.0
        
        st.session_state['persona'] = asyncio.run(PersonaService.list())[0]
        
        st.session_state['messages'] = []

    @property
    def model(self):
        return st.session_state.get('model', None)

    @model.setter
    def model(self, value):
        st.session_state['model'] = value
        
    @property
    def temperature(self):
        return st.session_state.get('temperature', 0.0)
    
    @temperature.setter
    def temperature(self, value):
        st.session_state['temperature'] = value
        
    @property
    def persona(self):
        return st.session_state.get('persona', None)
    
    @persona.setter
    def persona(self, value):
        st.session_state['persona'] = value
    
    @property
    def messages(self):
        return st.session_state['messages']
    
    @staticmethod
    def instance():
        if 'state_service' not in st.session_state:
            st.session_state['state_service'] = StateService()
        
        return st.session_state['state_service']