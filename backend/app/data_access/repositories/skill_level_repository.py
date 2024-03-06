from sqlalchemy.orm import Session
from app.data_access.models.skill_level import SkillLevel

class SkillLevelRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_level(self, level: str) -> SkillLevel:
        return self.session.query(SkillLevel).filter(SkillLevel.level == level).first()

    def get_all(self):
        return self.session.query(SkillLevel).all()