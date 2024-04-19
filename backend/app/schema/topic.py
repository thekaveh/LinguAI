from pydantic import BaseModel


class TopicBase(BaseModel):
    """
    Represents the base schema for a topic.

    Attributes:
        topic_name (str): The name of the topic.
    """
    topic_name: str


class TopicCreate(TopicBase):
    pass


class Topic(TopicBase):
    """
    Represents a topic.

    Attributes:
        topic_id (int): The ID of the topic.
    """

    topic_id: int

    class Config:
        from_attributes = True
