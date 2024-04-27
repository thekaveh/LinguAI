from typing import List
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.skill_level import SkillLevelSchema


class SkillLevelService:
    """
    This class provides methods to interact with the Skill Level service.
    """

    @log_decorator
    @staticmethod
    async def list() -> List[SkillLevelSchema]:
        """
        Retrieves a list of skill levels.

        Returns:
            A list of SkillLevelSchema objects representing the skill levels.
        """
        try:
            # Adjust Config.SKILL_LEVEL_SERVICE_LIST_ENDPOINT to your actual configuration
            skill_levels_list = await HttpUtils.get(
                Config.SKILL_LEVEL_SERVICE_LIST_ENDPOINT, response_model=List[SkillLevelSchema]
            )
            return skill_levels_list
        except Exception as e:
            raise e
        