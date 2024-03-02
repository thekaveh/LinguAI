# app/models/data_models/address.py

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .user import User

class Address(Base):
    __tablename__ = 'addresses'

    address_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("User", back_populates="addresses")
    address_type = Column(String(50))
    street = Column(String(255))
    door_number = Column(String(50))
    city = Column(String(100))
    state = Column(String(100))
    zip = Column(String(20))
    country = Column(String(100))