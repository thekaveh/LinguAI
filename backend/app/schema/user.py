from datetime import date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from .user_content import UserContentBase
from .user_topic import UserTopicBase
from .user_assessment import UserAssessmentBase

class UserBase(BaseModel):
    """
    Represents the base model for a user.

    Attributes:
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
        user_type (str): The type of user.
        base_language (Optional[str], optional): The base language of the user. Defaults to None.
        learning_languages (Optional[List[str]], optional): The list of languages the user is learning. Defaults to None.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        middle_name (Optional[str], optional): The middle name of the user. Defaults to None.
        preferred_name (Optional[str], optional): The preferred name of the user. Defaults to None.
        age (Optional[int], optional): The age of the user. Defaults to None.
        gender (Optional[str], optional): The gender of the user. Defaults to None.
        discovery_method (Optional[str], optional): The method through which the user discovered the platform. Defaults to None.
        motivation (Optional[str], optional): The user's motivation to use the platform. Defaults to None.
        mobile_phone (Optional[str], optional): The user's mobile phone number. Defaults to None.
        landline_phone (Optional[str], optional): The user's landline phone number. Defaults to None.
        contact_preference (Optional[str], optional): The user's preferred contact method. Defaults to None.
        user_topics (Optional[List[UserTopicBase]], optional): The list of topics associated with the user. Defaults to None.
        user_assessments (Optional[List[UserAssessmentBase]], optional): The list of assessments associated with the user. Defaults to None.
        user_contents (Optional[List[UserContentBase]], optional): The list of contents associated with the user. Defaults to None.
        enrollment_date (Optional[date], optional): The date of user enrollment. Defaults to None.
        last_login_date (Optional[date], optional): The date of user's last login. Defaults to None.
        consecutive_login_days (Optional[int], optional): The number of consecutive login days. Defaults to 0.
    """
    username: str
    email: EmailStr
    user_type: str
    base_language: Optional[str] = None
    learning_languages: Optional[List[str]] = None
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    preferred_name: Optional[str] = None # optional preferred name field
    age: Optional[int] = None # age field
    gender: Optional[str] = None 
    discovery_method: Optional[str] = None # optional field for "how did you hear about us?"
    motivation: Optional[str] = None # optional field for "what is your motivation to use the platform?"
    mobile_phone: Optional[str] = None
    landline_phone: Optional[str] = None
    contact_preference: Optional[str] = None
    user_topics: Optional[List[UserTopicBase]] = None
    user_assessments: Optional[List[UserAssessmentBase]] = None    
    user_contents: Optional[List[UserContentBase]] = None


    enrollment_date: Optional[date] = None
    last_login_date: Optional[date] = None
    consecutive_login_days: Optional[int] = Field(default=0, ge=0)
    


class UserCreate(UserBase):
    password_hash: str


class User(UserBase):
    """
    Represents a user in the system.

    Attributes:
        user_id (int): The unique identifier for the user.
    """
    user_id: int

    class Config:
        from_attributes = True
