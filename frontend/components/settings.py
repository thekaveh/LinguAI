import asyncio
import streamlit as st

from services.llm_service import LLMService
from services.state_service import StateService

def render():
    st.title("Settings")
    
    state_service = StateService.instance()
    llms = asyncio.run(LLMService.list())

    selected_llm = st.selectbox(
        "Select Large Language Model:"
        , llms
        , index=llms.index(state_service.selected_llm)
    )
    
    state_service.selected_llm = selected_llm