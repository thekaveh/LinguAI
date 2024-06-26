from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Topic(Base):
    """
    Represents a topic in the application.

    Attributes:
        topic_id (int): The unique identifier for the topic.
        topic_name (str): The name of the topic.
    """

    __tablename__ = 'topic'

    topic_id = Column(Integer, primary_key=True)
    topic_name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"<Topic(topic_id={self.topic_id}, topic_name={self.topic_name})>"