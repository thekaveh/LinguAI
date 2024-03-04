from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.repositories.data_access.session import get_db
from app.models.schema.prompt import PromptCreate, PromptUpdate, Prompt as PromptSchema, PromptSearch
from app.services.prompt_service import PromptService
from app.models.data_models.prompt import Prompt
from app.utils.logger import log_decorator  

router = APIRouter()

@log_decorator
@router.post("/prompts/", response_model=PromptSchema)
def create_prompt(prompt_create: PromptCreate, db: Session = Depends(get_db)):
    prompt_service = PromptService(db)
    return prompt_service.create_prompt(prompt_create)

@log_decorator
@router.get("/prompts/{prompt_id}", response_model=PromptSchema)
def read_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt_service = PromptService(db)
    prompt = prompt_service.get_prompt_by_id(prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@log_decorator
@router.get("/prompts/", response_model=List[PromptSchema])
def read_prompts(db: Session = Depends(get_db)):
    prompt_service = PromptService(db)
    return prompt_service.get_all_prompts()

@log_decorator
@router.post("/prompts/search", response_model=PromptSchema)
def search_prompt(prompt_search: PromptSearch, db: Session = Depends(get_db)):
    prompt_service = PromptService(db)
    prompt = prompt_service.get_prompt_by_search_criteria(prompt_search)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found based on search criteria")
    return prompt

@log_decorator
@router.put("/prompts/{prompt_id}", response_model=PromptSchema)
def update_prompt(prompt_id: int, prompt_update: PromptUpdate, db: Session = Depends(get_db)):
    prompt_service = PromptService(db)
    updated_prompt = prompt_service.update_prompt(prompt_id, prompt_update)
    if updated_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt

@log_decorator
@router.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt_service = PromptService(db)
    prompt_service.delete_prompt(prompt_id)
    return {"message": "Prompt deleted successfully"}
