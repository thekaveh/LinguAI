import streamlit as st

from utils.api_client import APIClient

def render():
    st.title("Settings")
    
    llms = APIClient.get_llms()
    if 'llm_type' not in st.session_state:    
        st.session_state['llm_type'] = llms[0]

    selected_llm_type = st.selectbox(
        "Select LLM Engine:"
        , llms
        , index=llms.index(st.session_state['llm_type'])
    )
    
    st.session_state['llm_type'] = selected_llm_type
