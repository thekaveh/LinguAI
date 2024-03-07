from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

from app.schema.language import Language

class UserAssessmentBase(BaseModel):
    assessment_date: date
    assessment_type: str
    skill_level: str
    strength: Optional[str] = None
    weakness: Optional[str] = None
    language: Language 

class UserAssessmentCreate(UserAssessmentBase):
    user_id: int
    language_id: int

class UserAssessment(UserAssessmentBase):
    assessment_id: int
    user_id: int

    class Config:
        orm_mode = True
