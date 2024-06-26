from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schema.user_content import UserContentBase, UserContentSearch, UserContent
from app.services.user_content_service import UserContentService 
from app.data_access.session import get_db
import logging
from app.core.config import Config

router = APIRouter()

logger = logging.getLogger(Config.BACKEND_LOGGER_NAME)
@router.post("/user-contents/", response_model=UserContent)
def create_user_content(user_content: UserContentBase, db: Session = Depends(get_db)):
    """
    Create a new user content.

    Args:
        user_content (UserContentBase): The user content data to be created.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        UserContent: The created user content.
    """
    logger.info(f"Creating user content: {user_content}")
    user_content_service = UserContentService(db)
    
    return user_content_service.create_user_content(user_content)

@router.post("/user-contents/search", response_model=List[UserContent])
def search_user_contents(search_params: UserContentSearch, db: Session = Depends(get_db)):
    """
    Search user contents based on the provided search parameters.

    Args:
        search_params (UserContentSearch): The search parameters for filtering user contents.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[UserContent]: A list of user contents that match the search criteria.
    """
    user_content_service = UserContentService(db)
    return user_content_service.read_user_content(search_params)

@router.delete("/user-contents/{content_id}", status_code=204)
def delete_user_content(content_id: int, db: Session = Depends(get_db)):
    """
    Delete user content by content ID.

    Args:
        content_id (int): The ID of the content to be deleted.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A dictionary with a success message.

    """
    logger.info(f"Deleting content with ID: {content_id}")
    user_content_service = UserContentService(db)
    user_content_service.delete_user_content(content_id)
    logger.info(f"Content with ID: {content_id} deleted successfully")
    return {"message": "Content deleted successfully"}
