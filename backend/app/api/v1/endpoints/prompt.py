from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.data_access.session import get_db
from app.utils.logger import log_decorator
from app.services.prompt_service import PromptService

from app.schema.prompt import (
    PromptCreate,
    PromptUpdate,
    Prompt as PromptSchema,
    PromptSearch,
)

router = APIRouter()


@log_decorator
@router.post("/prompts/", response_model=PromptSchema)
def create_prompt(prompt_create: PromptCreate, db: Session = Depends(get_db)):
    """
    Create a new prompt.

    Args:
        prompt_create (PromptCreate): The data required to create the prompt.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        PromptSchema: The created prompt.
    """
    prompt_service = PromptService(db)
    return prompt_service.create_prompt(prompt_create)


@log_decorator
@router.get("/prompts/{prompt_id}", response_model=PromptSchema)
def read_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a prompt by its ID.

    Args:
        prompt_id (int): The ID of the prompt to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        PromptSchema: The retrieved prompt.

    Raises:
        HTTPException: If the prompt is not found.
    """
    prompt_service = PromptService(db)
    prompt = prompt_service.get_prompt_by_id(prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@log_decorator
@router.get("/prompts/", response_model=List[PromptSchema])
def read_prompts(db: Session = Depends(get_db)):
    """
    Retrieve all prompts from the database.

    Parameters:
    - db: The database session.

    Returns:
    - A list of PromptSchema objects representing the prompts.
    """
    prompt_service = PromptService(db)
    return prompt_service.get_all_prompts()


@log_decorator
@router.post("/prompts/search", response_model=PromptSchema)
def search_prompt(prompt_search: PromptSearch, db: Session = Depends(get_db)):
    """
    Search for a prompt based on the given search criteria.

    Args:
        prompt_search (PromptSearch): The search criteria for the prompt.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        PromptSchema: The found prompt.

    Raises:
        HTTPException: If the prompt is not found based on the search criteria.
    """
    prompt_service = PromptService(db)
    prompt = prompt_service.get_prompt_by_search_criteria(prompt_search)
    if prompt is None:
        raise HTTPException(
            status_code=404, detail="Prompt not found based on search criteria"
        )
    return prompt


@log_decorator
@router.put("/prompts/{prompt_id}", response_model=PromptSchema)
def update_prompt(
    prompt_id: int, prompt_update: PromptUpdate, db: Session = Depends(get_db)
):
    """
    Update a prompt with the given prompt_id and prompt_update.

    Args:
        prompt_id (int): The ID of the prompt to be updated.
        prompt_update (PromptUpdate): The updated prompt data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        PromptSchema: The updated prompt.

    Raises:
        HTTPException: If the prompt is not found.
    """
    prompt_service = PromptService(db)
    updated_prompt = prompt_service.update_prompt(prompt_id, prompt_update)
    if updated_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt


@log_decorator
@router.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """
    Delete a prompt with the given prompt_id.

    Args:
        prompt_id (int): The ID of the prompt to be deleted.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A dictionary with a message indicating the prompt was deleted successfully.
    """
    prompt_service = PromptService(db)
    prompt_service.delete_prompt(prompt_id)
    return {"message": "Prompt deleted successfully"}
