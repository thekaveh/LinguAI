import asyncio
import requests

from typing import List, Tuple
from langserve import RemoteRunnable
from streamlit.delta_generator import DeltaGenerator
from langchain.prompts.chat import ChatPromptTemplate

from config import Config

class LLMService:
    @staticmethod
    async def achat(
		messages                : List[Tuple[str, str]]
		, message_placeholder   : DeltaGenerator
		, llm					: str
	) -> List[Tuple[str, str]]:
        chat_remote_runnable = RemoteRunnable(f"{Config.LLM_SERVICE_CHAT_BASE_ENDPOINT}/{llm}")
        
        full_response = ""
        
        if message_placeholder is not None:
            message_placeholder.markdown("Hmmmm...")
            
        async for chunk in chat_remote_runnable.astream(ChatPromptTemplate.from_messages(messages).format_messages()):
            full_response = full_response + chunk.content
            
            if message_placeholder is not None:
                message_placeholder.markdown(full_response + "▌")
                
        if message_placeholder is not None:
            message_placeholder.markdown(full_response)

        messages.append(("ai", full_response))
        
        return messages
    
    @staticmethod
    def list():
        response = requests.get(url=Config.LLM_SERVICE_LIST_ENDPOINT)
        return response.json().get("result", "") if response.status_code == 200 else "Error"
    
    @staticmethod
    def pull(model: str):
        response = requests.post(url=Config.LLM_SERVICE_PULL_ENDPOINT, json={"model": model})
        return response.json().get("result", "") if response.status_code == 200 else "Error"
