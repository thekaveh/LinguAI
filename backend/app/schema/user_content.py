from typing import Optional
from pydantic import BaseModel, Field
import datetime

class UserContentBase(BaseModel):
    """
    Represents the base model for user content.

    Attributes:
        user_id (int): The user ID this content belongs to.
        level (str, optional): The level of the user.
        language (str, optional): The language of the content.
        user_content (str, optional): The user's original content.
        gen_content (str, optional): The generated content.
        type (int, optional): The type of the content.
        created_date (datetime.datetime, optional): The creation date of the content.
        expiry_date (datetime.datetime, optional): The expiry date of the content.
    """
    user_id: int = Field(..., description="The user ID this content belongs to")
    level: Optional[str] = Field(None, description="The level of the user")
    language: Optional[str] = Field(None, description="The language of the content")
    user_content: Optional[str] = Field(None, description="The user's original content")
    gen_content: Optional[str] = Field(None, description="The generated content")
    type: Optional[int] = Field(None, description="The type of the content")
    created_date: Optional[datetime.datetime] = Field(None, description="The creation date of the content")
    expiry_date: Optional[datetime.datetime] = Field(None, description="The expiry date of the content")

class UserContentSearch(BaseModel):
    """
    Represents a search query for user content.

    Attributes:
        user_id (int): The ID of the user.
        content_type (int): The type of content to search for.
    """
    user_id: int
    content_type: int

class UserContent(UserContentBase):
    """
    Represents user content.

    Attributes:
        id (int): The ID of the user content.
    """
    id: int
    class Config:
        from_attributes = True