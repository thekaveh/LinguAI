import asyncio
import streamlit as st

from services.llm_service import LLMService
from services.state_service import StateService

async def achat(messages):
    state_service = StateService.instance()

    with st.chat_message("User"):
        st.markdown(messages[-1][1])

    with st.chat_message("AI"):
        response_message_placeholder = st.empty()

        messages = await LLMService.achat(
            messages=messages
            , model=state_service.get_selected_llm()
            , on_next_chunk=lambda chunk: response_message_placeholder.markdown(chunk)
        )

        st.session_state.messages = messages

    return messages

def render():
    state_service = StateService.instance()

    st.title(f"Chat with {state_service.get_selected_llm()}")
    
    for message in [m for m in state_service.messages if m[0] != "system"]:
        with st.chat_message(message[0]):
            st.markdown(message[1])
        
    if prompt := st.chat_input("Ask a question..."):
        state_service.messages.append(("user", prompt))
        
        asyncio.run(achat(state_service.messages))
