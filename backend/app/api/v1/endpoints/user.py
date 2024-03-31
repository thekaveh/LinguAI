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
    user_service = UserService(db)
    return user_service.get_users()


@log_decorator
@router.post("/users/", response_model=User)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_user(user_create)


@log_decorator
@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@log_decorator
@router.get("/users/username/{username}", response_model=User)
def read_user_by_username(username: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@log_decorator
@router.post("/users/{username}/topics", response_model=None)
def update_user_topics(
    username: str, new_topics: User, db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user_service.update_user_topics(username, new_topics)
    return None

@log_decorator
@router.post("/users/{user_id}/topics/{topic_name}", response_model=None)
def add_topic_to_user(user_id: int, topic_name: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user_service.add_topic_to_user(user_id, topic_name)
    return None


@log_decorator
@router.delete("/users/{user_id}/topics/{topic_name}", response_model=None)
def remove_topic_from_user(
    user_id: int, topic_name: str, db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user_service.remove_topic_from_user(user_id, topic_name)
    return None


@log_decorator
@router.get("/users/{user_id}/topics", response_model=list[Topic])
def read_user_topics(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_user_topics(user_id)


@log_decorator
@router.post("/users/authenticate")
def authenticate(
    request: AuthenticationRequest, db: Session = Depends(get_db)
) -> AuthenticationResponse:
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
    user_service = UserService(db)
    return user_service.create_user_assessment(user_id, assessment_data)


@log_decorator
@router.get(
    "/users/{user_id}/assessments/{assessment_id}", response_model=UserAssessment
)
def get_user_assessment(
    user_id: int, assessment_id: int, db: Session = Depends(get_db)
):
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
    user_service = UserService(db)
    return user_service.update_user_assessment(assessment_id, assessment_data)


@log_decorator
@router.delete("/users/{user_id}/assessments/{assessment_id}")
def delete_user_assessment(
    user_id: int, assessment_id: int, db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user_service.delete_user_assessment(assessment_id)
    return {"message": "User assessment deleted successfully"}

@log_decorator
@router.post("/users/{username}/languages", response_model=None)
def update_user_languages(username: str, user: User, db: Session = Depends(get_db)):
    user_service = UserService(db)
    try: 
        updated_user = user_service.update_user_languages(username, user)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@log_decorator
@router.post("/users/{username}/update", response_model=User)
def update_user_profile(username: str, user_update: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    try:
        updated_user = user_service.update_user_profile(username, user_update)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@log_decorator
@router.post("/users/{username}/change-password")
def change_user_password(password_change: PasswordChange, username: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    try:
        user_service.change_password(username, password_change.current_password, password_change.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@log_decorator
@router.delete("/users/{username}/delete")
def delete_user(username: str, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found")
