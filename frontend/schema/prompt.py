from typing import Optional
from pydantic import BaseModel


class PromptBase(BaseModel):
    prompt_text: str
    prompt_type: str
    prompt_category: str
    external_references: Optional[str] = None


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseModel):
    prompt_text: Optional[str] = None
    prompt_type: Optional[str] = None
    prompt_category: Optional[str] = None
    external_references: Optional[str] = None


class Prompt(PromptBase):
    prompt_id: int

    class Config:
        orm_mode = True


class PromptSearch(BaseModel):
    prompt_type: str
    prompt_category: str
