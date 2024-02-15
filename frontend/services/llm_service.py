import requests

from langserve import RemoteRunnable
from typing import List, Tuple, Callable
from langchain.prompts.chat import ChatPromptTemplate

from config import Config

class LLMService:
    @staticmethod
    async def achat(
        model: str
        , messages: List[Tuple[str, str]]
        , on_next_chunk: Callable[[str], None]
        , indicator: str = "▌"
    ) -> List[Tuple[str, str]]:
        chat_remote_runnable = RemoteRunnable(f"{Config.LLM_SERVICE_CHAT_BASE_ENDPOINT}/{model}")
        
        full_response = ""
        on_next_chunk(indicator)
        
        async for chunk in chat_remote_runnable.astream(ChatPromptTemplate.from_messages(messages).format_messages()):
            full_response += chunk.content

            on_next_chunk(full_response + indicator)

        on_next_chunk(full_response)

        messages.append(("ai", full_response))
        
        return messages
    
    @staticmethod
    def list():
        response = requests.get(url=Config.LLM_SERVICE_LIST_ENDPOINT)
        return response.json().get("result", "") if response.status_code == 200 else "Error"
