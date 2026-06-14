import pytest
from unittest.mock import MagicMock
from app.services.skill_level_service import SkillLevelService
from app.schema.skill_level import SkillLevelSchema

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def skill_level_service(mock_db_session):
    return SkillLevelService(mock_db_session)

def test_get_skill_level_by_level(skill_level_service, mock_db_session):
    mock_level = "Beginner"
    mock_db_skill_level = MagicMock()
    mock_db_skill_level.level = "Beginner"
    mock_db_skill_level.id = 1  # Provide a mock id attribute

    skill_level_service.skill_level_repo.get_by_level = MagicMock(return_value=mock_db_skill_level)

    retrieved_skill_level = skill_level_service.get_skill_level_by_level(mock_level)

    assert retrieved_skill_level.level == mock_db_skill_level.level

def test_get_all_skill_levels(skill_level_service, mock_db_session):
    mock_db_skill_levels = [MagicMock(), MagicMock()]
    for idx, mock_skill_level in enumerate(mock_db_skill_levels):
        mock_skill_level.level = f"Level {idx + 1}"
        mock_skill_level.id = idx + 1  # Provide mock id attributes

    skill_level_service.skill_level_repo.get_all = MagicMock(return_value=mock_db_skill_levels)

    retrieved_skill_levels = skill_level_service.get_all_skill_levels()

    assert len(retrieved_skill_levels) == len(mock_db_skill_levels)
    for idx, retrieved_skill_level in enumerate(retrieved_skill_levels):
        assert retrieved_skill_level.level == mock_db_skill_levels[idx].level
