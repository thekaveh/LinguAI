from typing import Optional
from pydantic import BaseModel


class PromptBase(BaseModel):
    """
    Represents the base model for a prompt.

    Attributes:
        prompt_text (str): The text of the prompt.
        prompt_type (str): The type of the prompt.
        prompt_category (str): The category of the prompt.
        external_references (Optional[str], optional): External references related to the prompt. Defaults to None.
    """
    prompt_text: str
    prompt_type: str
    prompt_category: str
    external_references: Optional[str] = None


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseModel):
    """
    Represents an update for a prompt.

    Attributes:
        prompt_text (Optional[str]): The updated prompt text.
        prompt_type (Optional[str]): The updated prompt type.
        prompt_category (Optional[str]): The updated prompt category.
        external_references (Optional[str]): The updated external references.
    """
    prompt_text: Optional[str] = None
    prompt_type: Optional[str] = None
    prompt_category: Optional[str] = None
    external_references: Optional[str] = None


class Prompt(PromptBase):
    """
    Represents a prompt.

    Attributes:
        prompt_id (int): The ID of the prompt.
    """

    prompt_id: int

    class Config:
        from_attributes = True


class PromptSearch(BaseModel):
    """
    Represents a search query for prompts.

    Attributes:
        prompt_type (str): The type of prompt.
        prompt_category (str): The category of prompt.
    """
    prompt_type: str
    prompt_category: str
