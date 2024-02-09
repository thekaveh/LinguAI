# pages/settings.py
import streamlit as st

def render():
    st.title("Settings")
    # Initialize session state for llm_type if not already set
    if 'llm_type' not in st.session_state:
        st.session_state['llm_type'] = 'openai'  # Default value
    
    # Selection box for llm_type in settings
    selected_llm_type = st.selectbox("Select LLM Type", ["openai", "local"], index=["openai", "local"].index(st.session_state['llm_type']))
    
    # Update session state with selected value
    st.session_state['llm_type'] = selected_llm_type
