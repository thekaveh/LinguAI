from typing import List, Optional
from sqlalchemy.orm import Session

from app.utils.logger import log_decorator
from app.data_access.models.prompt import Prompt
from app.schema.prompt import PromptCreate, PromptUpdate, PromptSearch
from app.data_access.repositories.prompt_repository import PromptRepository


class PromptService:
    """
    Service class for managing prompts.
    """

    @log_decorator
    def __init__(self, db_session: Session):
        self.prompt_repository = PromptRepository(db_session)

    @log_decorator
    def create_prompt(self, prompt_create: PromptCreate) -> Prompt:
        """
        Create a new prompt.

        Args:
            prompt_create (PromptCreate): The prompt data to create.

        Returns:
            Prompt: The created prompt.
        """
        return self.prompt_repository.create(prompt_create)

    @log_decorator
    def update_prompt(
        self, prompt_id: int, prompt_update: PromptUpdate
    ) -> Optional[Prompt]:
        """
        Update an existing prompt.

        Args:
            prompt_id (int): The ID of the prompt to update.
            prompt_update (PromptUpdate): The updated prompt data.

        Returns:
            Optional[Prompt]: The updated prompt if found, None otherwise.
        """
        existing_prompt = self.prompt_repository.find_by_prompt_id(prompt_id)
        if existing_prompt is None:
            return None
        return self.prompt_repository.update(existing_prompt, prompt_update)

    @log_decorator
    def delete_prompt(self, prompt_id: int) -> None:
        """
        Delete a prompt.

        Args:
            prompt_id (int): The ID of the prompt to delete.
        """
        self.prompt_repository.delete(prompt_id)

    @log_decorator
    def get_prompt_by_id(self, prompt_id: int) -> Optional[Prompt]:
        """
        Get a prompt by its ID.

        Args:
            prompt_id (int): The ID of the prompt to retrieve.

        Returns:
            Optional[Prompt]: The prompt if found, None otherwise.
        """
        return self.prompt_repository.find_by_prompt_id(prompt_id)

    @log_decorator
    def get_all_prompts(self) -> List[Prompt]:
        """
        Get all prompts.

        Returns:
            List[Prompt]: A list of all prompts.
        """
        return self.prompt_repository.find_all()

    @log_decorator
    def get_prompt_by_search_criteria(
        self, search_criteria: PromptSearch
    ) -> Optional[Prompt]:
        """
        Get a prompt by search criteria.

        Args:
            search_criteria (PromptSearch): The search criteria.

        Returns:
            Optional[Prompt]: The prompt if found, None otherwise.
        """
        return self.prompt_repository.find_by_search_criteria(search_criteria)
