from typing import List
from pydantic import BaseModel


class ListMessage(BaseModel):
    result: List[str]
