from pydantic import BaseModel

# CEFR skill levels, ordered. Single source of truth for the UI selectors.
SKILL_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


class SkillLevelBase(BaseModel):
    level: str


class SkillLevelCreate(SkillLevelBase):
    pass


class SkillLevelSchema(SkillLevelBase):
    id: int

    class Config:
        from_attributes = True
