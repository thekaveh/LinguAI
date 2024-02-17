from typing import List
from pydantic import BaseModel

class LLMListRes(BaseModel):
    result: List[str]
