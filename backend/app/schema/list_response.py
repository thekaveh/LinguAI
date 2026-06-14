from typing import List
from pydantic import BaseModel


class ListResponse(BaseModel):
    """
    Represents a response containing a list of strings.

    Attributes:
        result (List[str]): The list of strings in the response.
    """
    result: List[str]
