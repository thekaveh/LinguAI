from typing import List
from pydantic import BaseModel

class ListRes(BaseModel):
    result: List[str]
