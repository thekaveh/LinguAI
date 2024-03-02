from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.repositories.data_access.session import get_db
from app.models.schema.content import ContentCreate, Content as ContentSchema
from app.services.content_service import ContentService

router = APIRouter()

@router.get("/contents/list", response_model=list[ContentSchema])
def read_contents(db: Session = Depends(get_db)):
    content_service = ContentService(db)
    return content_service.get_all_content()

@router.post("/contents/", response_model=ContentSchema)
def create_content(content_create: ContentCreate, db: Session = Depends(get_db)):
    content_service = ContentService(db)
    return content_service.create_content(content_create)

@router.get("/contents/{content_id}", response_model=ContentSchema)
def read_content(content_id: int, db: Session = Depends(get_db)):
    content_service = ContentService(db)
    content = content_service.get_content_by_id(content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.put("/contents/{content_id}", response_model=ContentSchema)
def update_content(content_id: int, content_update: ContentCreate, db: Session = Depends(get_db)):
    content_service = ContentService(db)
    updated_content = content_service.update_content(content_id, content_update)
    if updated_content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return updated_content

@router.delete("/contents/{content_id}")
def delete_content(content_id: int, db: Session = Depends(get_db)):
    content_service = ContentService(db)
    content_service.delete_content(content_id)
    return {"message": "Content deleted successfully"}
