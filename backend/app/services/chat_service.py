from typing import AsyncIterable, List, Tuple

from app.services.llm_service import LLMService

class ChatService:
    @staticmethod
    async def achat(messages: List[Tuple[str, str]], model: str, temperature: float = 0) -> AsyncIterable[str]:
        return (
            chunk.content async for chunk in LLMService.get_runnable(
                model=model
                , temperature=temperature
            ).astream(messages)
        )