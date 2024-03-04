from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.utils.logger import log_decorator
from app.data_access.session import get_db
from app.services.content_service import ContentService
from app.schema.content import ContentCreate, Content as ContentSchema

router = APIRouter()


@log_decorator
@router.get("/contents/list", response_model=list[ContentSchema])
def read_contents(db: Session = Depends(get_db)):
    content_service = ContentService(db)
    return content_service.get_all_content()


@log_decorator
@router.post("/contents/", response_model=ContentSchema)
def create_content(content_create: ContentCreate, db: Session = Depends(get_db)):
    content_service = ContentService(db)
    return content_service.create_content(content_create)


@log_decorator
@router.get("/contents/{content_id}", response_model=ContentSchema)
def read_content(content_id: int, db: Session = Depends(get_db)):
    content_service = ContentService(db)
    content = content_service.get_content_by_id(content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@log_decorator
@router.put("/contents/{content_id}", response_model=ContentSchema)
def update_content(
    content_id: int, content_update: ContentCreate, db: Session = Depends(get_db)
):
    content_service = ContentService(db)
    updated_content = content_service.update_content(content_id, content_update)
    if updated_content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return updated_content


@log_decorator
@router.delete("/contents/{content_id}")
def delete_content(content_id: int, db: Session = Depends(get_db)):
    content_service = ContentService(db)
    content_service.delete_content(content_id)
    return {"message": "Content deleted successfully"}
