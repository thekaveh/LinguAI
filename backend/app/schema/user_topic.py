from pydantic import BaseModel


class UserTopicBase(BaseModel):
    """
    Represents the base model for a user topic.

    Attributes:
        user_id (int): The ID of the user.
        topic_name (str): The name of the topic.
    """
    user_id: int
    topic_name: str


class UserTopicCreate(UserTopicBase):
    pass


class UserTopic(UserTopicBase):
    """
    Represents a user topic.

    Attributes:
        id (int): The unique identifier for the user topic.
    """

    id: int

    class Config:
        from_attributes = True
