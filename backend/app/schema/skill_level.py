from pydantic import BaseModel


class SkillLevelBase(BaseModel):
    level: str


class SkillLevelCreate(SkillLevelBase):
    pass


class SkillLevelSchema(SkillLevelBase):
    """
    Represents a schema for the skill level of a particular skill.
    """

    id: int

    class Config:
        from_attributes = True
