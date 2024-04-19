from typing import List
from pydantic import BaseModel

from .content import Content
from .language import Language


class ContentGenReq(BaseModel):
    """
    Represents a request for content generation.

    Attributes:
        user_id (int): The ID of the user making the request.
        user_topics (List[str]): The topics provided by the user.
        content (Content): The content object containing the details of the content to be generated.
        language (Language): The language in which the content should be generated.
        skill_level (str): The skill level required for the generated content.
        llm_id (int): The ID of the language learning model to be used for content generation.
        temperature (float): The temperature parameter for controlling the randomness of the generated content.
    """
    user_id: int
    user_topics: List[str]
    content: Content
    language: Language
    skill_level: str
    llm_id: int
    temperature: float


class ContentGenRes(BaseModel):
    """
    Represents the response from the content generation process.

    Attributes:
        generated_content (str): The generated content.
    """
    generated_content: str
