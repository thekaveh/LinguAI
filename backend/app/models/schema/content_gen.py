from pydantic import BaseModel
from typing import List
from .content import Content
from .language import Language
from .user_topic import UserTopic

class ContentGenReq(BaseModel):
    user_id: int
    user_topics: List[str]
    content: Content
    language: Language

class ContentGenRes(BaseModel):
    generated_content: str
