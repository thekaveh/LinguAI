from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Prompt(Base):
    """
    Represents a prompt entity in the database.

    Attributes:
        prompt_id (int): The unique identifier for the prompt.
        prompt_text (str): The text of the prompt.
        prompt_type (str): The type of the prompt.
        prompt_category (str): The category of the prompt.
        external_references (str): Any external references related to the prompt.
    """

    __tablename__ = 'prompts'

    prompt_id = Column(Integer, primary_key=True)
    prompt_text = Column(Text, nullable=False)
    prompt_type = Column(String(100), nullable=False)
    prompt_category = Column(String(100), nullable=False)
    external_references = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Prompt(prompt_id={self.prompt_id}, prompt_text={self.prompt_text}, prompt_type={self.prompt_type}, prompt_category={self.prompt_category}, external_references={self.external_references})>"