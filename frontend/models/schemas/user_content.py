from typing import Optional
from pydantic import BaseModel, Field
import datetime

class UserContentBase(BaseModel):
#    id: Optional[int] = Field(None, description="The ID of the user content")
    user_id: int = Field(..., description="The user ID this content belongs to")
    level: Optional[str] = Field(None, description="The level of the user")
    language: Optional[str] = Field(None, description="The language of the content")
    user_content: Optional[str] = Field(None, description="The user's original content")
    gen_content: Optional[str] = Field(None, description="The generated content")
    type: Optional[int] = Field(None, description="The type of the content")
    created_date: Optional[datetime.datetime] = Field(None, description="The creation date of the content")
    expiry_date: Optional[datetime.datetime] = Field(None, description="The expiry date of the content")

class UserContentSearch(BaseModel):
    user_id: int
    content_type:int

class UserContent(UserContentBase):
    id: int
    class Config:
        from_attributes = True