from typing import List
from pydantic import BaseModel

from .content import Content
from .language import Language


class ContentGenReq(BaseModel):
    user_id: int
    user_topics: List[str]
    content: Content
    language: Language
    skill_level: str
    model_name: str
    temperature: float    

class ContentGenRes(BaseModel):
    generated_content: str
