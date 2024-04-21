import logging
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schema.topic import Topic
from app.utils.logger import log_decorator
from app.data_access.session import get_db
from app.schema.user import User, UserCreate
from app.schema.password_change import PasswordChange
from app.services.user_service import UserService
from app.schema.user_assessment import UserAssessment, UserAssessmentCreate
from app.schema.authentication import AuthenticationRequest, AuthenticationResponse
from app.data_access.models.user import User as UserModel

router = APIRouter()

@log_decorator
@router.get("/users/list", response_model=list[User])
def read_users(db: Session = Depends(get_db)):
    """
    Retrieve a list of users from the database.

    Parameters:
    - db: The database session.

    Returns:
    - A list of User objects.
    """
    user_service = UserService(db)
    return user_service.get_users()


@log_decorator
@router.post("/users/", response_model=User)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        user_create (UserCreate): The user data to create.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The created user.
    """
    user_service = UserService(db)
    return user_service.create_user(user_create)


@log_decorator
@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a user by their ID.

    Args:
        user_id (int): The ID of the user to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The user object.

    Raises:
        HTTPException: If the user is not found.
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@log_decorator
@router.get("/users/username/{username}", response_model=User)
def read_user_by_username(username: str, db: Session = Depends(get_db)):
    """
    Retrieve a user by their username.

    Args:
        username (str): The username of the user to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The user object.

    Raises:
        HTTPException: If the user is not found.
    """
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@log_decorator
@router.get("/users/username/{username}/id", response_model=int)
def read_user_id_by_username(username:str, db: Session = Depends(get_db)):
    """
    Retrieve the user ID by username.

    Args:
        username (str): The username of the user.

    Returns:
        int: The user ID.

    Raises:
        HTTPException: If the user is not found.
    """
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user.user_id

@log_decorator
@router.post("/users/{username}/topics", response_model=None)
def update_user_topics(
    username: str, new_topics: User, db: Session = Depends(get_db)
):
    """
    Update the topics of a user.

    Args:
        username (str): The username of the user.
        new_topics (User): The updated topics for the user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        None
    """
    user_service = UserService(db)
    user_service.update_user_topics(username, new_topics)
    return None

@log_decorator
@router.post("/users/{user_id}/topics/{topic_name}", response_model=None)
def add_topic_to_user(user_id: int, topic_name: str, db: Session = Depends(get_db)):
    """
    Add a topic to a user.

    Args:
        user_id (int): The ID of the user.
        topic_name (str): The name of the topic to be added.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        None
    """
    user_service = UserService(db)
    user_service.add_topic_to_user(user_id, topic_name)
    return None


@log_decorator
@router.delete("/users/{user_id}/topics/{topic_name}", response_model=None)
def remove_topic_from_user(
    user_id: int, topic_name: str, db: Session = Depends(get_db)
):
    """
    Removes a topic from a user.

    Args:
        user_id (int): The ID of the user.
        topic_name (str): The name of the topic to be removed.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        None
    """
    user_service = UserService(db)
    user_service.remove_topic_from_user(user_id, topic_name)
    return None


@log_decorator
@router.get("/users/{user_id}/topics", response_model=list[Topic])
def read_user_topics(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the topics associated with a specific user.

    Args:
        user_id (int): The ID of the user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        list[Topic]: A list of topics associated with the user.
    """
    user_service = UserService(db)
    return user_service.get_user_topics(user_id)


@log_decorator
@router.post("/users/authenticate")
def authenticate(
    request: AuthenticationRequest, db: Session = Depends(get_db)
) -> AuthenticationResponse:
    """
    Authenticates a user based on the provided request.

    Args:
        request (AuthenticationRequest): The authentication request containing user credentials.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        AuthenticationResponse: The authentication response containing user information and access token.

    Raises:
        HTTPException: If an error occurs during authentication.
    """
    try:
        service = UserService(db)
        return service.authenticate(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add routes for CRUD operations on user_assessment
@log_decorator
@router.post("/users/{user_id}/assessments/", response_model=UserAssessment)
def create_user_assessment(
    user_id: int, assessment_data: UserAssessmentCreate, db: Session = Depends(get_db)
):
    """
    Create a new user assessment.

    Args:
        user_id (int): The ID of the user.
        assessment_data (UserAssessmentCreate): The data for the user assessment.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        UserAssessment: The created user assessment.
    """
    user_service = UserService(db)
    return user_service.create_user_assessment(user_id, assessment_data)


@log_decorator
@router.get(
    "/users/{user_id}/assessments/{assessment_id}", response_model=UserAssessment
)
def get_user_assessment(
    user_id: int, assessment_id: int, db: Session = Depends(get_db)
):
    """
    Retrieve a user's assessment by user ID and assessment ID.

    Parameters:
    - user_id (int): The ID of the user.
    - assessment_id (int): The ID of the assessment.
    - db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    - UserAssessment: The user's assessment.

    """
    user_service = UserService(db)
    return user_service.get_user_assessment(assessment_id)


@log_decorator
@router.put(
    "/users/{user_id}/assessments/{assessment_id}", response_model=UserAssessment
)
def update_user_assessment(
    user_id: int,
    assessment_id: int,
    assessment_data: UserAssessmentCreate,
    db: Session = Depends(get_db),
):
    """
    Update a user's assessment.

    Args:
        user_id (int): The ID of the user.
        assessment_id (int): The ID of the assessment.
        assessment_data (UserAssessmentCreate): The data for the updated assessment.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        UserAssessment: The updated user assessment.
    """
    user_service = UserService(db)
    return user_service.update_user_assessment(assessment_id, assessment_data)


@log_decorator
@router.delete("/users/{user_id}/assessments/{assessment_id}")
def delete_user_assessment(
    user_id: int, assessment_id: int, db: Session = Depends(get_db)
):
    """
    Delete a user assessment.

    Args:
        user_id (int): The ID of the user.
        assessment_id (int): The ID of the assessment to be deleted.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A dictionary with a success message.
    """
    user_service = UserService(db)
    user_service.delete_user_assessment(assessment_id)
    return {"message": "User assessment deleted successfully"}

@log_decorator
@router.post("/users/{username}/languages", response_model=None)
def update_user_languages(username: str, user: User, db: Session = Depends(get_db)):
    """
    Update the languages of a user.

    Args:
        username (str): The username of the user.
        user (User): The user object containing the updated language information.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Updated user object.

    Raises:
        HTTPException: If there is an error updating the user's languages.
    """
    user_service = UserService(db)
    try: 
        updated_user = user_service.update_user_languages(username, user)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@log_decorator
@router.post("/users/{username}/update", response_model=User)
def update_user_profile(username: str, user_update: UserCreate, db: Session = Depends(get_db)):
    """
    Update the profile of a user.

    Args:
        username (str): The username of the user to update.
        user_update (UserCreate): The updated user information.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The updated user profile.

    Raises:
        HTTPException: If the user is not found.
    """
    user_service = UserService(db)
    try:
        updated_user = user_service.update_user_profile(username, user_update)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@log_decorator
@router.post("/users/{username}/change-password")
def change_user_password(password_change: PasswordChange, username: str, db: Session = Depends(get_db)):
    """
    Change the password for a user.

    Args:
        password_change (PasswordChange): The password change request model.
        username (str): The username of the user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If there is an error changing the password.

    Returns:
        None
    """
    user_service = UserService(db)
    try:
        user_service.change_password(username, password_change.current_password, password_change.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@log_decorator
@router.delete("/users/{username}/delete")
def delete_user(username: str, db: Session = Depends(get_db)):
    """
    Delete a user from the database.

    Args:
        username (str): The username of the user to be deleted.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the user is not found in the database.

    Returns:
        None
    """
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found")