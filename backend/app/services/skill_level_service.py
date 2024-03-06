from sqlalchemy.orm import Session
from typing import List, Optional
from app.data_access.repositories.skill_level_repository import SkillLevelRepository
from app.data_access.models.skill_level import SkillLevel
from app.schema.skill_level import SkillLevelSchema

class SkillLevelService:
    def __init__(self, db_session: Session):
        self.skill_level_repo = SkillLevelRepository(db_session)

    def get_skill_level_by_level(self, level: str) -> Optional[SkillLevelSchema]:
        skill_level = self.skill_level_repo.get_by_level(level)
        if skill_level:
            return SkillLevelSchema(**skill_level.__dict__)
        return None

    def get_all_skill_levels(self) -> List[SkillLevelSchema]:
        skill_levels = self.skill_level_repo.get_all()
        return [SkillLevelSchema(**skill_level.__dict__) for skill_level in skill_levels]