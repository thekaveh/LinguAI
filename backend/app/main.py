from fastapi import FastAPI
from sqlmodel import Session

from app.core.config import Config
from app.services.llm_service import LLMService
from app.api.v1.router import router as v1_router
from app.services.dependency.db_service import init_db
from app.utils.logger_config import setup_global_logging
from app.services.dependency.db_service import db_engine

# Setup global logging with a specific logger name
setup_global_logging(
    logger_name=Config.BACKEND_LOGGER_NAME,
    log_filename=Config.BACKEND_LOG_FILE,
    log_level=Config.BACKEND_LOG_LEVEL,
)

app = FastAPI()
app.include_router(v1_router)


@app.on_event("startup")
def on_startup():
    init_db()

    with Session(db_engine) as db_session:
        LLMService(db_session=db_session).init_ollama()
