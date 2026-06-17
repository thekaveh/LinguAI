from pydantic import BaseModel



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
