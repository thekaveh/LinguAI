# pages/home.py
import streamlit as st
from utils.api_client import APIClient

def render():
    st.title("Home")
    input_text = st.text_input("Enter your text:", "Ice cream")

    # Use llm_type from session state, default to 'openai' if not set
    llm_type = st.session_state.get('llm_type', 'openai')
    
    if st.button("Call HTTP POST"):
        with st.spinner("Processing..."):
            post_result = APIClient.call_joke_service(input_text, llm_type)
            st.text_area("POST Response", value=post_result, height=200)
