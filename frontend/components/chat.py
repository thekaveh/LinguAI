import streamlit as st
from langserve import RemoteRunnable
from langchain.prompts.chat import ChatPromptTemplate
import asyncio
from typing import List, Tuple
from streamlit.delta_generator import DeltaGenerator

from config import Config

ollama_llm = RemoteRunnable(f"{Config.BACKEND_ENDPOINT}/v1/llm/ollama")

async def run_conversation(
    messages                : List[Tuple[str, str]]
    , message_placeholder   : DeltaGenerator
) -> List[Tuple[str, str]]:
    full_response = ""

    if message_placeholder is not None:
        message_placeholder.markdown("Hmmmm...")
        
    async for chunk in ollama_llm.astream(ChatPromptTemplate.from_messages(messages).format_messages()):
        full_response = full_response + chunk
        
        if message_placeholder is not None:
            message_placeholder.markdown(full_response + "▌")

    if message_placeholder is not None:
        message_placeholder.markdown(full_response)

    messages.append(("ai", full_response))

    return messages

async def chat(messages):
    with st.chat_message("User"):
        st.markdown(messages[-1][1])

    with st.chat_message("AI"):
        message_placeholder = st.empty()

        messages = await run_conversation(messages, message_placeholder)
        st.session_state.messages = messages
    return messages

def render():
    """Display the chat interface and handle user input using a form."""
    if 'messages' not in st.session_state:
        st.session_state.messages = [
        (
            "system"
            , """
				You are a highly educated linguaphile and helpful person who loves to use big, sarcastic words.
				You are also concise and precise.
            """
        )
    ]
    
    # Display chat history excluding system messages for UI
    for message in [m for m in st.session_state.messages if m[0] != "system"]:
        with st.chat_message(message[0]):
            st.markdown(message[1])
        
    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append(("user", prompt))
        
        asyncio.run(chat(st.session_state.messages))
