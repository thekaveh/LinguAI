from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class UserContent(Base):
    __tablename__ = 'user_contents'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Fixed syntax error
    level = Column(String(255))
    language = Column(String(255))
    user_content = Column(Text)
    gen_content = Column(Text)
    type = Column(Integer)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    expiry_date = Column(DateTime)
