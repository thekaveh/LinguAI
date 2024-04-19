from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class UserContent(Base):
    """
    Represents user-generated content.

    Attributes:
        id (int): The unique identifier for the user content.
        user_id (int): The ID of the user who generated the content.
        level (str): The level of the content.
        language (str): The language of the content.
        user_content (str): The user-generated content.
        gen_content (str): The generated content.
        type (int): The type of the content.
        created_date (datetime): The date and time when the content was created.
        expiry_date (datetime): The date and time when the content will expire.
    """

    __tablename__ = 'user_contents'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    level = Column(String(255))
    language = Column(String(255))
    user_content = Column(Text)
    gen_content = Column(Text)
    type = Column(Integer)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    expiry_date = Column(DateTime)
