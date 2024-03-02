from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.repositories.data_access.session import get_db
from app.models.schema.user import User, UserCreate
from app.models.schema.topic import Topic
from app.services.user_service import UserService

router = APIRouter()

@router.get("/users/list", response_model=list[User])
def read_users(db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_users()

@router.post("/users/", response_model=User)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_user(user_create)

@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}/topics", response_model=None)
def update_user_topics(user_id: int, new_topics: list[str], db: Session = Depends(get_db)):
    user_service = UserService(db)
    user_service.update_user_topics(user_id, new_topics)
    return None

@router.post("/users/{user_id}/topics/{topic_name}", response_model=None)
def add_topic_to_user(user_id: int, topic_name: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user_service.add_topic_to_user(user_id, topic_name)
    return None

@router.delete("/users/{user_id}/topics/{topic_name}", response_model=None)
def remove_topic_from_user(user_id: int, topic_name: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user_service.remove_topic_from_user(user_id, topic_name)
    return None

@router.get("/users/{user_id}/topics", response_model=list[Topic])
def read_user_topics(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_user_topics(user_id)
