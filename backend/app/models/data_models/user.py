from sqlalchemy import Column, String, Integer, ARRAY
from .base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    # User identification
    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    # Authentication
    password_hash = Column(String(100), nullable=False)

    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))

    # Contact information
    mobile_phone = Column(String(20))
    landline_phone = Column(String(20))
    contact_preference = Column(String(50))  # e.g., 'email', 'mobile_phone'

    # User settings and preferences
    user_type = Column(String(100), nullable=False)  # Changed from Enum to String
    base_language = Column(String(100))  # Changed from Enum to String
    learning_languages = Column(ARRAY(String))  # Changed from ARRAY(Enum) to ARRAY(String)
    
    # Add this line to create a bidirectional relationship
    addresses = relationship("Address", back_populates="user")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}', user_type='{self.user_type}', first_name='{self.first_name}', last_name='{self.last_name}', contact_preference='{self.contact_preference}')>"