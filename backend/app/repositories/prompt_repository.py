from app.models.schema.prompt import PromptCreate, PromptUpdate, PromptSearch
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.data_models.prompt import Prompt

class PromptRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def find_by_prompt_id(self, prompt_id: int) -> Optional[Prompt]:
        return self.db_session.query(Prompt).filter(Prompt.prompt_id == prompt_id).first()

    def find_by_search_criteria(self, search_criteria: PromptSearch) -> Optional[Prompt]:
        return self.db_session.query(Prompt).filter(
            Prompt.prompt_type == search_criteria.prompt_type, 
            Prompt.prompt_category == search_criteria.prompt_category
        ).first()

    def find_all(self) -> List[Prompt]:
        return self.db_session.query(Prompt).all()

    def create(self, prompt_create: PromptCreate) -> Prompt:
        new_prompt = Prompt(
            prompt_text=prompt_create.prompt_text,
            prompt_type=prompt_create.prompt_type,
            prompt_category=prompt_create.prompt_category,
            external_references=prompt_create.external_references
        )
        self.db_session.add(new_prompt)
        self.db_session.commit()
        self.db_session.refresh(new_prompt)
        return new_prompt

    def update(self, prompt: Prompt, prompt_update: PromptUpdate) -> Prompt:
        # Update the fields of `prompt` with values from `prompt_update`
        update_data = prompt_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(prompt, key, value)
        self.db_session.commit()
        self.db_session.refresh(prompt)
        return prompt

    def delete(self, prompt_id: int) -> None:
        prompt = self.find_by_prompt_id(prompt_id)
        if prompt:
            self.db_session.delete(prompt)
            self.db_session.commit()