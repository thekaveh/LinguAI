from pydantic import BaseModel


class ContentRewriteReq(BaseModel):
    user_id: int
    language: str
    skill_level: str
    input_content: str