from pydantic import BaseModel

from .user_assessment import UserAssessmentBase


class ReviewWritingReq(BaseModel):
    """
    Represents a request for writing a review.

    Attributes:
        user_id (int): The ID of the user.
        language (str): The language of the content being reviewed.
        curr_skill_level (str): The current skill level of the user.
        next_skill_level (str): The desired skill level of the user after the review.
        strength (str): The strengths of the user's content.
        weakness (str): The weaknesses of the user's content.
        input_content (str): The content to be reviewed.
        llm_id (int): The ID of the language model used for the review.
        temperature (float): The temperature parameter for generating the review.
    """
    user_id: int
    language: str
    curr_skill_level: str
    next_skill_level: str
    strength: str
    weakness: str
    input_content: str
    llm_id: int
    temperature: float
