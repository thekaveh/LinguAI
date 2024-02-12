import streamlit as st

from services.state_service import StateService

def render():
    st.title("Settings")
    
    state_service = StateService.instance()

    selected_llm = st.selectbox(
        "Select LLM:"
        , state_service.get_llms()
        , index=state_service.get_llms().index(state_service.get_selected_llm())
    )
    
    state_service.set_selected_llm(selected_llm)
