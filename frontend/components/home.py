import streamlit as st

from utils.api_client import APIClient

def render():
    st.title("Home")
    input_text = st.text_input("Enter your text:", "Ice cream")

    llm_type = st.session_state.get('llm_type', 'litellm')
    
    if st.button("Call HTTP POST"):
        with st.spinner("Processing..."):
            post_result = APIClient.call_joke_service(input_text, llm_type)
            st.text_area("POST Response", value=post_result, height=200)
