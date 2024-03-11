from pydantic import BaseModel


class ContentBase(BaseModel):
    content_name: str


class ContentCreate(BaseModel):
    content_name: str


class Content(ContentBase):
    content_id: int

    class Config:
        from_attributes = True
