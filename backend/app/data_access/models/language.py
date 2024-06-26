from sqlalchemy import Column, Integer, String
from .base import Base

class Language(Base):
    """
    Represents a language in the system.

    Attributes:
        language_id (int): The unique identifier for the language.
        language_name (str): The name of the language.
    """

    __tablename__ = 'language'

    language_id = Column(Integer, primary_key=True)
    language_name = Column(String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"<Language(language_id={self.language_id}, language_name='{self.language_name}')>"
