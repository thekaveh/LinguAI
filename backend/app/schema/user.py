from typing import List, Optional
from pydantic import BaseModel, EmailStr


class UserTopicBase(BaseModel):
    topic_name: str


class UserBase(BaseModel):
    username: str
    email: EmailStr
    user_type: str
    base_language: Optional[str] = None
    learning_languages: Optional[List[str]] = None
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    mobile_phone: Optional[str] = None
    landline_phone: Optional[str] = None
    contact_preference: Optional[str] = None
    user_topics: Optional[List[UserTopicBase]] = None

class UserCreate(UserBase):
    password_hash: str


class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True
