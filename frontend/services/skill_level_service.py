from typing import List
from core.config import Config
from utils.logger import log_decorator
from utils.http_utils import HttpUtils
from schema.skill_level import SkillLevelSchema


class SkillLevelService:
    @log_decorator
    @staticmethod
    async def list() -> List[SkillLevelSchema]:
        try:
            # Adjust Config.SKILL_LEVEL_SERVICE_LIST_ENDPOINT to your actual configuration
            skill_levels_list = await HttpUtils.get(
                Config.SKILL_LEVEL_SERVICE_LIST_ENDPOINT, response_model=List[SkillLevelSchema]
            )
            return skill_levels_list
        except Exception as e:
            raise e
        