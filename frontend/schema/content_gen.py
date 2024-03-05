from typing import List
from pydantic import BaseModel

from schema.content import Content
from schema.language import Language


class ContentGenReq(BaseModel):
    user_id: int
    user_topics: List[str]
    content: Content
    language: Language


class ContentGenRes(BaseModel):
    generated_content: str
