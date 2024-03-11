from pydantic import BaseModel


class UserTopicBase(BaseModel):
    user_id: int
    topic_name: str


class UserTopicCreate(UserTopicBase):
    pass


class UserTopic(UserTopicBase):
    id: int

    class Config:
        from_attributes = True
