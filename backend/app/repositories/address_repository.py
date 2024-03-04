from app.utils.logger import log_decorator
from .base_repository import BaseRepository
from sqlalchemy.orm import Session
from app.models.data_models.address import Address as DBAddress
from app.models.schema.address import AddressUpdate

class AddressRepository(BaseRepository[DBAddress]):
    @log_decorator    
    def __init__(self, db_session: Session):
        super().__init__(db_session, DBAddress)
        
    @log_decorator        
    def update(self, address_id: int, address_update: AddressUpdate) -> DBAddress:
        db_address = self.get_by_id(address_id)
        if db_address:
            for field, value in address_update.dict(exclude_unset=True).items():
                setattr(db_address, field, value)
            self.db_session.commit()
            self.db_session.refresh(db_address)
        return db_address