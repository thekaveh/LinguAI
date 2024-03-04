from typing import List, Optional
from sqlalchemy.orm import Session

from app.utils.logger import log_decorator
from app.data_access.models.prompt import Prompt
from app.schema.prompt import PromptCreate, PromptUpdate, PromptSearch
from app.data_access.repositories.prompt_repository import PromptRepository


class PromptService:
    @log_decorator
    def __init__(self, db_session: Session):
        self.prompt_repository = PromptRepository(db_session)

    @log_decorator
    def create_prompt(self, prompt_create: PromptCreate) -> Prompt:
        return self.prompt_repository.create(prompt_create)

    @log_decorator
    def update_prompt(
        self, prompt_id: int, prompt_update: PromptUpdate
    ) -> Optional[Prompt]:
        existing_prompt = self.prompt_repository.find_by_prompt_id(prompt_id)
        if existing_prompt is None:
            return None
        return self.prompt_repository.update(existing_prompt, prompt_update)

    @log_decorator
    def delete_prompt(self, prompt_id: int) -> None:
        self.prompt_repository.delete(prompt_id)

    @log_decorator
    def get_prompt_by_id(self, prompt_id: int) -> Optional[Prompt]:
        return self.prompt_repository.find_by_prompt_id(prompt_id)

    @log_decorator
    def get_all_prompts(self) -> List[Prompt]:
        return self.prompt_repository.find_all()

    @log_decorator
    def get_prompt_by_search_criteria(
        self, search_criteria: PromptSearch
    ) -> Optional[Prompt]:
        return self.prompt_repository.find_by_search_criteria(search_criteria)
