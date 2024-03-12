from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import Config

db_engine = create_engine(Config.DATABASE_URL, echo=True)

def init_db() -> None:
	SQLModel.metadata.create_all(db_engine)

def get_db_session() -> Session:        
    with Session(db_engine) as session:
        yield session
