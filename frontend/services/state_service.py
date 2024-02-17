import asyncio
import streamlit as st

from services.llm_service import LLMService

class StateService:
    def __init__(self):
        st.session_state['model'] = asyncio.run(LLMService.list())[0]
        st.session_state['temperature'] = 0.0
        st.session_state.messages = [
			(
				"system"
				, """
					You are a highly educated, sharp tongued linguaphile and a helpful, sharp witted assistant called LinguAI who loves to use big, sarcastic words and yet strives to be concise, precise, and to the point.
					Do try and use emojis to convey your emotions instead of stating them explicitly.
				"""
			)
		]

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
    def messages(self):
        return st.session_state.messages
    
    @staticmethod
    def instance():
        if 'state_service' not in st.session_state:
            st.session_state['state_service'] = StateService()
        
        return st.session_state['state_service']