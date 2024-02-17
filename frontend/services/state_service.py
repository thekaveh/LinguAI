import asyncio
import streamlit as st

from services.llm_service import LLMService

class StateService:
    def __init__(self):
        self._initialize_llms()

        st.session_state.messages = [
			(
				"system"
				, """
					You are a highly educated, sharp tongued linguaphile and a helpful, sharp witted assistant called LinguAI who loves to use big, sarcastic words and yet strives to be concise, precise, and to the point.
					Do try and use emojis to convey your emotions instead of stating them explicitly.
				"""
			)
		]
        
    def _initialize_llms(self):
        llms = asyncio.run(LLMService.list())
        st.session_state['selected_llm'] = llms[0] if llms else None

    @property
    def selected_llm(self):
        return st.session_state.get('selected_llm', None)

    @selected_llm.setter
    def selected_llm(self, value):
        st.session_state['selected_llm'] = value
    
    @property
    def messages(self):
        return st.session_state.messages
    
    @staticmethod
    def instance():
        if 'state_service' not in st.session_state:
            st.session_state['state_service'] = StateService()
        
        return st.session_state['state_service']