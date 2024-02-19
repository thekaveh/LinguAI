from pydantic import BaseModel
from typing import List, Tuple

class ChatReq(BaseModel):
    model		: str
    messages	: List[Tuple[str, str]]
    temperature	: float 				= 0.0
    persona		: str 					= "Neutral"
