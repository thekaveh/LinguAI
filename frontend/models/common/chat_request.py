from typing import List
from pydantic import BaseModel

from models.common.chat_message import ChatMessage


class ChatRequest(BaseModel):
    model: str

    messages: List[ChatMessage]

    persona: str = "Neutral"
    temperature: float = 0.0
