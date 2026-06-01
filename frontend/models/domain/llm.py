from __future__ import annotations
from pydantic import BaseModel, Field


class LLM(BaseModel):
    """
    Represents a Language Learning Model (LLM).

    Attributes:
        id (int): The unique identifier for the LLM.
        is_active (bool): Indicates whether the LLM is active or not.
        vision (int): The vision score of the LLM.
        content (int): The content score of the LLM.
        structured_content (int): The structured content score of the LLM.
        embeddings (int): The embeddings score of the LLM.
        provider (str): The provider of the LLM.
        name (str): The name of the LLM.

    Methods:
        display_name(): Returns the display name of the LLM.
    """

    id: int = Field(...)
    is_active: bool = Field(default=False)
    vision: int = Field(default=-1)
    content: int = Field(default=-1)
    structured_content: int = Field(default=-1)
    embeddings: int = Field(default=-1)
    provider: str = Field(...)
    name: str = Field(...)

    def display_name(self) -> str:
        """
        Returns the display name of the LLM.

        Returns:
            str: The display name of the LLM in the format "{name} | {provider}".
        """
        return f"{self.name} | {self.provider}"
