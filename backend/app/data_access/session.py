from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import Config


engine = create_engine(Config.DATABASE_URL, echo=True)  # echo=True for debugging
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Returns a database session.

    Yields:
        SessionLocal: The database session.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
