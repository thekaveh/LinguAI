from pydantic import BaseModel


class ContentRewriteReq(BaseModel):
    """
    Represents a request for content rewriting.

    Attributes:
        user_id (int): The ID of the user making the request.
        language (str): The target language for the content rewriting.
        skill_level (str): The desired skill level for the rewritten content.
        input_content (str): The content to be rewritten.
        llm_id (int): The ID of the language model to be used for rewriting.
        temperature (float): The temperature parameter for the rewriting process.
        user_skill_level (str): The skill level of the user making the request.
        user_base_language (str): The base language of the user making the request.
    """
    user_id: int
    language: str
    skill_level: str
    input_content: str
    llm_id: int
    temperature: float
    user_skill_level: str
    user_base_language: str
