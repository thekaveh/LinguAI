import streamlit as st

from services.llm_service import LLMService

class StateService:
    def __init__(self):
        st.session_state['llms'] = LLMService.list()
        st.session_state['selected_llm'] = st.session_state['llms'][0]
    
    def get_llms(self):
        return st.session_state['llms']
    
    def get_selected_llm(self):
        return st.session_state['selected_llm']
    
    def set_selected_llm(self, value):
        st.session_state['selected_llm'] = value
    
    @staticmethod
    def instance():
        if 'state_service' not in st.session_state:
            st.session_state['state_service'] = StateService()
        
        return st.session_state['state_service']