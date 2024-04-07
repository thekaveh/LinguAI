from typing import Optional, List
from sqlalchemy import desc
from sqlalchemy.orm import Session
from pydantic import parse_obj_as
import logging
from app.core.config import Config
from app.data_access.models.user_content import UserContent as UserContentModel
from app.schema.user_content import UserContentBase, UserContentSearch, UserContent

class UserContentService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(Config.BACKEND_LOGGER_NAME)
    def create_user_content(self, user_content_data: UserContentBase) -> UserContent:
        self.logger.info(f"Creating user content: {user_content_data}")
        user_content_dict = user_content_data.dict(exclude_none=True)
        user_content = UserContentModel(**user_content_dict)
        self.db.add(user_content)
        self.db.commit()
        self.db.refresh(user_content)
        self.logger.info(f"User content created with ID: {user_content.id}")
        return UserContent.from_orm(user_content)

    def read_user_content_v0(self, search_params: UserContentSearch) -> List[UserContent]:
        query = self.db.query(UserContentModel).filter(UserContentModel.user_id == search_params.user_id)
        if search_params.content_type is not None:
            query = query.filter(UserContentModel.type == search_params.content_type)
        user_contents = query.all()
        return parse_obj_as(List[UserContent], user_contents)
    
    def delete_user_content(self, content_id: int) -> None:
        self.logger.info(f"Deleting content with ID: {content_id}")
        user_content = self.db.query(UserContentModel).filter(UserContentModel.id == content_id).first()
        if user_content:
            self.db.delete(user_content)
            self.db.commit()

    def read_user_content(self, search_params: UserContentSearch) -> List[UserContent]:
        query = self.db.query(UserContentModel).filter(UserContentModel.user_id == search_params.user_id)
        
        if search_params.content_type is not None:
            query = query.filter(UserContentModel.type == search_params.content_type)
        
        # Sort results by created_date in descending order
        query = query.order_by(desc(UserContentModel.created_date))
        
        user_contents = query.all()
        return parse_obj_as(List[UserContent], user_contents)            