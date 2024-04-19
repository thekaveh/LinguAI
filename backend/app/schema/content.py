from pydantic import BaseModel


class ContentBase(BaseModel):
    """
    Base model for content.
    """
    content_name: str


class ContentCreate(BaseModel):
    """
    Represents the data required to create a new content.

    Attributes:
        content_name (str): The name of the content.
    """
    content_name: str


class Content(ContentBase):
    """
    Represents a content object.

    Attributes:
        content_id (int): The ID of the content.
    """

    content_id: int

    class Config:
        from_attributes = True
