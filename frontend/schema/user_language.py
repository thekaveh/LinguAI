from pydantic import BaseModel

class UserLanguage(BaseModel):
    user_id: int
    language_id: int