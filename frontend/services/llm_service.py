import requests

# from langserve import RemoteRunnable
from typing import List, Tuple, Callable
# from langchain.prompts.chat import ChatPromptTemplate

from config import Config
from utils.http_utils import HttpUtils
from models.shared.request_models.ChatRequest import ChatRequest

class LLMService:
    @staticmethod
    async def achat(
        model			: str
        , messages		: List[Tuple[str, str]]
        , on_next_chunk	: Callable[[str], None]
        , indicator		: str = "▌"
    ) -> List[Tuple[str, str]]:
        full_response = ""
        on_next_chunk(indicator)

        async for chunk in HttpUtils.apost_stream(
            url=Config.LLM_SERVICE_CHAT_ENDPOINT
            , request=ChatRequest(
				model=model
				, messages=messages
				, temperature=0
			)
        ):
            full_response += chunk

            on_next_chunk(full_response + indicator)

        on_next_chunk(full_response)

        messages.append(("ai", full_response))
        
        return messages
    
    @staticmethod
    def list():
        response = requests.get(url=Config.LLM_SERVICE_LIST_ENDPOINT)
        return response.json().get("result", "") if response.status_code == 200 else "Error"
