from typing import List
from pydantic import BaseModel


class ListResponse(BaseModel):
    result: List[str]
