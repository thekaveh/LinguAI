from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

from .language import Language


class UserAssessmentBase(BaseModel):
    """
    Represents the base model for a user assessment.

    Attributes:
        assessment_date (datetime): The date of the assessment.
        assessment_type (str): The type of assessment.
        skill_level (str): The skill level of the user.
        strength (Optional[str], optional): The user's strength. Defaults to None.
        weakness (Optional[str], optional): The user's weakness. Defaults to None.
        language (Language): The language of the assessment.
    """
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
    """
    Represents a user assessment.

    Attributes:
        assessment_id (int): The ID of the assessment.
        user_id (int): The ID of the user.

    Config:
        from_attributes (bool): Indicates whether to load attributes from the database.
    """
    assessment_id: int
    user_id: int

    class Config:
        from_attributes = True
