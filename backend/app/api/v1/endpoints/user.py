from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from app.schema.topic import Topic
from app.utils.logger import log_decorator
from app.data_access.session import get_db
from app.schema.user import User, UserBase, UserCreate
from app.schema.user_topic import UserTopicBase
from app.schema.password_change import PasswordChange
from app.services.user_service import UserService
from app.schema.user_assessment import UserAssessment, UserAssessmentCreate
from app.schema.authentication import AuthenticationRequest, AuthenticationResponse

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
    username: str, new_topics: list[UserTopicBase], db: Session = Depends(get_db)
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


def _load_owned_assessment(service: UserService, user_id: int, assessment_id: int):
    """Fetch an assessment and verify it belongs to ``user_id``.

    Raises 404 if the assessment is missing or owned by a different user;
    keeps the failure mode identical between "no such row" and "row exists
    but wrong owner" to avoid leaking row presence.
    """
    db_assessment = service.get_user_assessment(assessment_id)
    if db_assessment is None or getattr(db_assessment, "user_id", None) != user_id:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return db_assessment


@log_decorator
@router.get(
    "/users/{user_id}/assessments/{assessment_id}", response_model=UserAssessment
)
def get_user_assessment(
    user_id: int, assessment_id: int, db: Session = Depends(get_db)
):
    """
    Retrieve a user's assessment by user ID and assessment ID.
    """
    user_service = UserService(db)
    return _load_owned_assessment(user_service, user_id, assessment_id)


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
    Update a user's assessment. 404 if the assessment doesn't belong to ``user_id``.
    """
    user_service = UserService(db)
    _load_owned_assessment(user_service, user_id, assessment_id)
    updated = user_service.update_user_assessment(assessment_id, assessment_data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return updated


@log_decorator
@router.delete(
    "/users/{user_id}/assessments/{assessment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_assessment(
    user_id: int, assessment_id: int, db: Session = Depends(get_db)
):
    """
    Delete a user assessment. 404 if the assessment doesn't belong to ``user_id``.
    """
    user_service = UserService(db)
    _load_owned_assessment(user_service, user_id, assessment_id)
    if not user_service.delete_user_assessment(assessment_id):
        raise HTTPException(status_code=404, detail="Assessment not found")
    return None

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
def update_user_profile(username: str, user_update: UserBase, db: Session = Depends(get_db)):
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
@router.delete("/users/{username}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(username: str, db: Session = Depends(get_db)):
    """
    Delete a user from the database. Returns 404 if the user does not exist.
    """
    user_service = UserService(db)
    if not user_service.delete_user_by_username(username):
        raise HTTPException(status_code=404, detail="User not found")
    return None