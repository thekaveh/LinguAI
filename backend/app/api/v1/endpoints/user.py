import logging
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.schema.topic import Topic
from app.utils.logger import log_decorator
from app.data_access.session import get_db
from app.schema.user import User, UserCreate
from app.services.user_service import UserService
from app.schema.login_request import LoginRequest
from app.schema.user_assessment import UserAssessment, UserAssessmentCreate

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
@router.put("/users/{user_id}/topics", response_model=None)
def update_user_topics(
    user_id: int, new_topics: list[str], db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user_service.update_user_topics(user_id, new_topics)
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
def authenticate(login_request: LoginRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)
    auth_result = user_service.authenticate_user(login_request.username, login_request.password)
    if auth_result is None:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    if "error" in auth_result:
        raise HTTPException(status_code=401, detail=auth_result["error"])
    return auth_result

# Add routes for CRUD operations on user_assessment
@log_decorator
@router.post("/users/{user_id}/assessments/", response_model=UserAssessment)
def create_user_assessment(user_id: int, assessment_data: UserAssessmentCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_user_assessment(user_id, assessment_data)

@log_decorator
@router.get("/users/{user_id}/assessments/{assessment_id}", response_model=UserAssessment)
def get_user_assessment(user_id: int, assessment_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_user_assessment(assessment_id)

@log_decorator
@router.put("/users/{user_id}/assessments/{assessment_id}", response_model=UserAssessment)
def update_user_assessment(user_id: int, assessment_id: int, assessment_data: UserAssessmentCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.update_user_assessment(assessment_id, assessment_data)

@log_decorator
@router.delete("/users/{user_id}/assessments/{assessment_id}")
def delete_user_assessment(user_id: int, assessment_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user_service.delete_user_assessment(assessment_id)
    return {"message": "User assessment deleted successfully"}