from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SkillLevel(Base):
    __tablename__ = 'skill_level'

    id = Column(Integer, primary_key=True)
    level = Column(String)

    def __repr__(self):
        return f"<SkillLevel(id={self.id}, level={self.level})>"