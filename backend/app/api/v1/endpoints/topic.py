from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.utils.logger import log_decorator

from app.data_access.session import get_db
from app.services.topic_service import TopicService
from app.schema.topic import TopicCreate, Topic as TopicSchema

router = APIRouter()


@log_decorator
@router.get("/topics/list", response_model=list[TopicSchema])
def read_topics(db: Session = Depends(get_db)):
    """
    Retrieve a list of all topics.

    Parameters:
    - db: The database session.

    Returns:
    - A list of TopicSchema objects representing the topics.
    """
    topic_service = TopicService(db)
    return topic_service.get_all_topics()


@log_decorator
@router.post("/topics/", response_model=TopicSchema)
def create_topic(topic_create: TopicCreate, db: Session = Depends(get_db)):
    """
    Create a new topic.

    Args:
        topic_create (TopicCreate): The data required to create a new topic.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        TopicSchema: The created topic.
    """
    topic_service = TopicService(db)
    return topic_service.create_topic(topic_create)


@log_decorator
@router.get("/topics/{topic_id}", response_model=TopicSchema)
def read_topic(topic_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific topic by its ID.

    Args:
        topic_id (int): The ID of the topic to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        TopicSchema: The retrieved topic.

    Raises:
        HTTPException: If the topic is not found.
    """
    topic_service = TopicService(db)
    topic = topic_service.get_topic_by_id(topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@log_decorator
@router.put("/topics/{topic_id}", response_model=TopicSchema)
def update_topic(
    topic_id: int, topic_update: TopicCreate, db: Session = Depends(get_db)
):
    """
    Update a topic with the given topic_id.

    Args:
        topic_id (int): The ID of the topic to be updated.
        topic_update (TopicCreate): The updated topic data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        TopicSchema: The updated topic.
    
    Raises:
        HTTPException: If the topic with the given topic_id is not found.
    """
    topic_service = TopicService(db)
    updated_topic = topic_service.update_topic(topic_id, topic_update)
    if updated_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return updated_topic


@log_decorator
@router.delete("/topics/{topic_id}")
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    """
    Delete a topic by its ID.

    Args:
        topic_id (int): The ID of the topic to be deleted.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A dictionary with a message indicating the success of the deletion.
    """
    topic_service = TopicService(db)
    topic_service.delete_topic(topic_id)
    return {"message": "Topic deleted successfully"}
