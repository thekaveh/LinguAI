from sqlmodel import Session, SQLModel, create_engine

from app.core.config import Config

db_engine = create_engine(Config.DATABASE_URL, echo=True)


def init_db() -> None:
    """
    Note: Half way through the project we came across SQLModel that was more concise and worked efficiently with FastAPI.
    We decided to switch to SQLModel and implement the necessary changes to the codebase.
    This is the new implementation of the database service.

    Initializes the database by creating all the tables defined in the SQLModel metadata.

    Returns:
        None
    """
    SQLModel.metadata.create_all(db_engine)


def get_db_session() -> Session:
    """
    Note: Half way through the project we came across SQLModel that was more concise and worked efficiently with FastAPI.
    We decided to switch to SQLModel and implement the necessary changes to the codebase.
    This is the new implementation of Session. If there is a case where the service needs both ORMs pay attention to Tx.

    Returns a database session using the specified database engine.

    Returns:
        Session: The database session object.
    """
    with Session(db_engine) as session:
        yield session
