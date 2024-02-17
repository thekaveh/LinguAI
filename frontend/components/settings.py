import asyncio
import streamlit as st

from services.llm_service import LLMService
from services.state_service import StateService

def render():
    st.title("Settings")
    
    state_service = StateService.instance()

    with st.expander("LLM", expanded=True):
        st.markdown("<hr>", unsafe_allow_html=True)
        
        models = asyncio.run(LLMService.list())
        
        new_model = st.selectbox(
			label="Model:"
			, options=models
   			, key="llm.model"
			, index=models.index(state_service.model)
		)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        new_temperature = st.slider(
            step=0.1
            , min_value=0.0
            , max_value=1.0
            , label="Temperature:"
            , key="llm.temperature"
            , value=state_service.temperature
        )
        
        state_service.model = new_model
        state_service.temperature = new_temperature
   