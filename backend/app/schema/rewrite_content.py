from pydantic import BaseModel
from app.schema.language import Language

class ContentRewriteReq(BaseModel):
    user_id: int
    language: str
    skill_level: str
    input_content: str