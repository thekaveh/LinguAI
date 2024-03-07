from pydantic import BaseModel

class SkillLevelBase(BaseModel):
    level: str

class SkillLevelCreate(SkillLevelBase):
    pass

class SkillLevelSchema(SkillLevelBase):
    id: int

    class Config:
        orm_mode = True