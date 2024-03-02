from pydantic import BaseModel

class LanguageBase(BaseModel):
    language_name: str

class LanguageCreate(LanguageBase):
    pass

class Language(LanguageBase):
    language_id: int

    class Config:
        orm_mode = True