from sqlalchemy.orm import relationship
from sqlalchemy import Column, Date, String, Integer, ARRAY, ForeignKey, Text

from .base import Base
from app.data_access.models.language import Language

class User(Base):
    __tablename__ = "users"

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
    contact_preference = Column(String(50))

    # User settings and preferences
    user_type = Column(String(100), nullable=False)
    base_language = Column(String(100))
    learning_languages = Column(
        ARRAY(String)
    )

    # User topics relationship
    user_topics = relationship("UserTopic", back_populates="user")
    
    user_assessments = relationship("UserAssessment", back_populates="user")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}', user_type='{self.user_type}', first_name='{self.first_name}', last_name='{self.last_name}', contact_preference='{self.contact_preference}')>"

class UserTopic(Base):
    __tablename__ = "user_topics"

    # User topic identification
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    topic_name = Column(String(100), primary_key=True, nullable=False)

    # Define relationship
    user = relationship("User", back_populates="user_topics")

    def __repr__(self):
        return f"<UserTopic(user_id={self.user_id}, topic_name='{self.topic_name}')>"

class UserAssessment(Base):
    __tablename__ = "user_assessment"

    assessment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    assessment_date = Column(Date)
    language_id = Column(Integer, ForeignKey("language.language_id"))
    assessment_type = Column(String(100))
    skill_level = Column(String(100))
    strength = Column(Text)
    weakness = Column(Text)

    # Define relationship with User table
    user = relationship("User", back_populates="user_assessments")

    # Define relationship with Language table
    language = relationship("Language") 
    # Define relationship with Language table
    #language = relationship("Language", back_populates="user_assessments")