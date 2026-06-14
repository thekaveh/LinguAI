from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Content(Base):
    """
    Represents a piece of content.

    Attributes:
        content_id (int): The unique identifier for the content.
        content_name (str): The name of the content.
    """
    __tablename__ = 'content'

    content_id = Column(Integer, primary_key=True)
    content_name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"<Content(content_id={self.content_id}, content_name={self.content_name})>"