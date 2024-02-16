from pydantic import BaseModel
from typing import List, Tuple

class ChatRequest(BaseModel):
    model		: str
    messages	: List[Tuple[str, str]]
    temperature	: float = 0.0
