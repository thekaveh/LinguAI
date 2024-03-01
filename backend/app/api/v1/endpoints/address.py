from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.repositories.data_access.session import get_db
from app.models.schema.address import Address, AddressCreate, AddressUpdate
from app.services.address_service import AddressService

router = APIRouter()

@router.get("/addresses/list", response_model=List[Address])
def list_addresses(db: Session = Depends(get_db)):
    address_service = AddressService(db)
    return address_service.get_addresses()

@router.post("/addresses/", response_model=Address)
def create_address(address_create: AddressCreate, db: Session = Depends(get_db)):
    address_service = AddressService(db)
    return address_service.create_address(address_create)

@router.get("/addresses/{address_id}", response_model=Address)
def get_address(address_id: int, db: Session = Depends(get_db)):
    address_service = AddressService(db)
    address = address_service.get_address_by_id(address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.put("/addresses/{address_id}", response_model=Address)
def update_address(address_id: int, address_update: AddressUpdate, db: Session = Depends(get_db)):
    address_service = AddressService(db)
    updated_address = address_service.update_address(address_id, address_update)
    if updated_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return updated_address
