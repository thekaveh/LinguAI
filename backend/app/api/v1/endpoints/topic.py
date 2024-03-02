from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.repositories.data_access.session import get_db
from app.models.schema.topic import TopicCreate, Topic as TopicSchema
from app.services.topic_service import TopicService

router = APIRouter()

@router.get("/topics/list", response_model=list[TopicSchema])
def read_topics(db: Session = Depends(get_db)):
    topic_service = TopicService(db)
    return topic_service.get_all_topics()

@router.post("/topics/", response_model=TopicSchema)
def create_topic(topic_create: TopicCreate, db: Session = Depends(get_db)):
    topic_service = TopicService(db)
    return topic_service.create_topic(topic_create)

@router.get("/topics/{topic_id}", response_model=TopicSchema)
def read_topic(topic_id: int, db: Session = Depends(get_db)):
    topic_service = TopicService(db)
    topic = topic_service.get_topic_by_id(topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.put("/topics/{topic_id}", response_model=TopicSchema)
def update_topic(topic_id: int, topic_update: TopicCreate, db: Session = Depends(get_db)):
    topic_service = TopicService(db)
    updated_topic = topic_service.update_topic(topic_id, topic_update)
    if updated_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return updated_topic

@router.delete("/topics/{topic_id}")
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    topic_service = TopicService(db)
    topic_service.delete_topic(topic_id)
    return {"message": "Topic deleted successfully"}