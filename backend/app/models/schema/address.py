from pydantic import BaseModel
from typing import Optional

class AddressBase(BaseModel):
    address_type: str
    street: str
    door_number: str
    city: str
    state: str
    zip: str
    country: str

class AddressCreate(BaseModel):
    address: AddressBase
    user_id: int

class Address(AddressBase):
    address_id: int
    user_id: int

    class Config:
        orm_mode = True
        
class AddressUpdate(BaseModel):
    address_type: Optional[str]
    street: Optional[str]
    door_number: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    country: Optional[str]