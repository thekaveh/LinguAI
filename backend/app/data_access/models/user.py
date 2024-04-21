from sqlalchemy.orm import relationship
from sqlalchemy import Column, Date, String, Integer, ARRAY, ForeignKey, Text, DateTime

from .base import Base
from app.data_access.models.language import Language


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        user_id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password_hash (str): The hashed password of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        middle_name (str): The middle name of the user.
        preferred_name (str): The preferred name of the user.
        age (int): The age of the user.
        gender (str): The gender of the user.
        discovery_method (str): The method through which the user discovered the system.
        motivation (str): The motivation of the user for using the system.
        mobile_phone (str): The mobile phone number of the user.
        landline_phone (str): The landline phone number of the user.
        contact_preference (str): The preferred method of contact for the user.
        user_type (str): The type of user (e.g., admin, regular user).
        base_language (str): The base language of the user.
        learning_languages (list): The list of languages the user is learning.
        enrollment_date (date): The date when the user enrolled in the system.
        last_login_date (date): The date of the user's last login.
        consecutive_login_days (int): The number of consecutive days the user has logged in.
        user_topics (list): The list of topics associated with the user.
        user_assessments (list): The list of assessments associated with the user.
    """

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    preferred_name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(50))
    discovery_method = Column(String(100))
    motivation = Column(Text)
    mobile_phone = Column(String(20))
    landline_phone = Column(String(20))
    contact_preference = Column(String(50))
    user_type = Column(String(100), nullable=False)
    base_language = Column(String(100))
    learning_languages = Column(ARRAY(String))
    enrollment_date = Column(Date)
    last_login_date = Column(Date)
    consecutive_login_days = Column(Integer, default=0)
    user_topics = relationship("UserTopic", back_populates="user", cascade='all, delete-orphan')
    user_assessments = relationship("UserAssessment", back_populates="user", cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}', user_type='{self.user_type}', first_name='{self.first_name}', last_name='{self.last_name}', contact_preference='{self.contact_preference}')>"


class UserTopic(Base):
    """
    Represents a user topic in the application.

    Attributes:
        user_id (int): The ID of the user associated with the topic.
        topic_name (str): The name of the topic.

    Relationships:
        user (User): The user object associated with the topic.

    Methods:
        __repr__(): Returns a string representation of the UserTopic object.
    """

    __tablename__ = "user_topics"

    # User topic identification
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    topic_name = Column(String(100), primary_key=True, nullable=False)

    # Define relationship
    user = relationship("User", back_populates="user_topics")

    def __repr__(self):
        return f"<UserTopic(user_id={self.user_id}, topic_name='{self.topic_name}')>"


class UserAssessment(Base):
    """
    Represents a user assessment.

    Attributes:
        assessment_id (int): The ID of the assessment.
        user_id (int): The ID of the user associated with the assessment.
        assessment_date (datetime): The date of the assessment.
        language_id (int): The ID of the language associated with the assessment.
        assessment_type (str): The type of the assessment.
        skill_level (str): The skill level of the user in the assessment.
        strength (str): The strengths identified in the assessment.
        weakness (str): The weaknesses identified in the assessment.
        user (User): The user associated with the assessment.
        language (Language): The language associated with the assessment.
    """

    __tablename__ = "user_assessment"

    assessment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    assessment_date = Column(DateTime)
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
    # language = relationship("Language", back_populates="user_assessments")