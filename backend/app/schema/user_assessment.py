from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

from .language import Language


class UserAssessmentBase(BaseModel):
    assessment_date: datetime
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
        from_attributes = True
