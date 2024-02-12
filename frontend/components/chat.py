import asyncio
import streamlit as st

from services.llm_service import LLMService
from services.state_service import StateService

async def achat(messages):
    state_service = StateService.instance()

    with st.chat_message("User"):
        st.markdown(messages[-1][1])

    with st.chat_message("AI"):
        message_placeholder = st.empty()

        messages = await LLMService.achat(messages, message_placeholder, llm=state_service.get_selected_llm())
        st.session_state.messages = messages
    return messages

def render():
    state_service = StateService.instance()

    st.title(f"Chat with {state_service.get_selected_llm()}")

    if 'messages' not in st.session_state:
        st.session_state.messages = [
        (
            "system"
            , """
				You are a highly educated, sharp tongued linguaphile and a helpful, sharp witted assistant called LinguAI who loves to use big, sarcastic words and yet strives to be concise, precise, and to the point.
				Do try and use emojis to convey your emotions instead of stating them explicitly.
            """
        )
    ]
    
    for message in [m for m in st.session_state.messages if m[0] != "system"]:
        with st.chat_message(message[0]):
            st.markdown(message[1])
        
    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append(("user", prompt))
        
        asyncio.run(achat(st.session_state.messages))
