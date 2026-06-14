from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.data_access.session import get_db
from app.services.skill_level_service import SkillLevelService
from app.schema.skill_level import SkillLevelSchema

router = APIRouter()

@router.get("/skill_levels/list", response_model=list[SkillLevelSchema])
def read_skill_levels(db: Session = Depends(get_db)):
    """
    Retrieve all skill levels.

    Returns a list of all skill levels available in the database.

    Parameters:
    - db (Session): The database session to use for querying.

    Raises:
    - HTTPException: If no skill levels are found in the database.

    Returns:
    - list[SkillLevelSchema]: A list of skill levels retrieved from the database.
    """
    skill_level_service = SkillLevelService(db)
    skill_levels = skill_level_service.get_all_skill_levels()
    if not skill_levels:
        raise HTTPException(status_code=404, detail="No skill levels found")
    return skill_levels

@router.get("/skill_levels/{level}", response_model=SkillLevelSchema)
def get_skill_level_by_level(level: str, db: Session = Depends(get_db)):
    """
    Retrieve a skill level by its level.

    Parameters:
    - level (str): The level of the skill.

    Returns:
    - SkillLevelSchema: The skill level object.

    Raises:
    - HTTPException: If the skill level is not found.

    """
    skill_level_service = SkillLevelService(db)
    skill_level = skill_level_service.get_skill_level_by_level(level)
    if not skill_level:
        raise HTTPException(status_code=404, detail=f"Skill level '{level}' not found")
    return skill_level