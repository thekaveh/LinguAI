# app/services/address_service.py

from sqlalchemy.orm import Session
from app.models.data_models.address import Address
from app.models.schema.address import Address as AddressSchema, AddressCreate, AddressUpdate
from app.repositories.address_repository import AddressRepository

class AddressService:
    def __init__(self, db: Session):
        self.db = db

    def create_address(self, address_create: AddressCreate) -> AddressSchema:
        return AddressRepository(self.db).create(address_create)

    def get_address_by_id(self, address_id: int) -> AddressSchema:
        return AddressRepository(self.db).get_by_id(address_id)
    """ 
    def get_addresses(self) -> list[Address]:
        return AddressRepository(self.db).get_all()
    """
    
    def get_addresses(self):
        return self.db.query(Address).all()

    def update_address(self, address_id: int, address_update: AddressUpdate) -> AddressSchema:
        return AddressRepository(self.db).update(address_id, address_update)
