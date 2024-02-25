from pydantic import BaseModel, Field
from typing import List, Tuple, Optional


class ChatMessage(BaseModel):
    model: str

    messages: List[Tuple[str, str]]
    images: Optional[List[str]] = None

    persona: str = "Neutral"
    temperature: float = 0.0
