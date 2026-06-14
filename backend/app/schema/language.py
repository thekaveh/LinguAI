from pydantic import BaseModel


class LanguageBase(BaseModel):
    """
    Represents the base model for a language.

    Attributes:
        language_name (str): The name of the language.
    """
    language_name: str


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(LanguageBase):
    pass


class Language(LanguageBase):
    """
    Represents a language with additional properties.

    Attributes:
        language_id (int): The unique identifier for the language.
    """

    language_id: int

    class Config:
        from_attributes = True
