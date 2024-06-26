from pydantic import BaseModel

from .user_assessment import UserAssessmentBase


class ReviewWritingReq(BaseModel):
    user_id: int
    language: str
    # user_assessment: UserAssessmentBase
    curr_skill_level: str
    next_skill_level: str
    strength: str
    weakness: str
    input_content: str
    llm_id: int
    temperature: float
