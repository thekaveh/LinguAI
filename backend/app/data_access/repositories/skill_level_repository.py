from sqlalchemy.orm import Session
from app.data_access.models.skill_level import SkillLevel

class SkillLevelRepository:
    """
    Repository class for accessing SkillLevel objects in the database.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_by_level(self, level: str) -> SkillLevel:
        """
        Retrieve a SkillLevel object by its level.

        Args:
            level (str): The level of the skill.

        Returns:
            SkillLevel: The SkillLevel object matching the specified level, or None if not found.
        """
        return self.session.query(SkillLevel).filter(SkillLevel.level == level).first()

    def get_all(self):
        """
        Retrieves all skill levels from the database.

        Returns:
            A list of SkillLevel objects representing all skill levels in the database.
        """
        return self.session.query(SkillLevel).all()
