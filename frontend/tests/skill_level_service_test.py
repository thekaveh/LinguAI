import pytest
from unittest.mock import AsyncMock
from services.skill_level_service import SkillLevelService
from typing import List
from core.config import Config
from utils.http_utils import HttpUtils
from schema.skill_level import SkillLevelSchema

@pytest.mark.asyncio
async def test_list_skill_levels_success():
    # Mocks
    expected_skill_levels = [SkillLevelSchema(id=1, level="beginner"), SkillLevelSchema(id=2, level="intermediate")]
    HttpUtils.get = AsyncMock(return_value=expected_skill_levels)

    # Test
    skill_levels = await SkillLevelService.list()

    # Assertions
    assert all(skill_level in skill_levels for skill_level in expected_skill_levels)
    HttpUtils.get.assert_awaited_once_with(Config.SKILL_LEVEL_SERVICE_LIST_ENDPOINT, response_model=List[SkillLevelSchema])

@pytest.mark.asyncio
async def test_list_skill_levels_failure():
    # Mocks
    HttpUtils.get = AsyncMock(side_effect=Exception("Test Exception"))

    # Test and Assertions
    with pytest.raises(Exception, match="Test Exception"):
        await SkillLevelService.list()
