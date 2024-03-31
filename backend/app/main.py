from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import Session
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(v1_router)
background_scheduler = BackgroundScheduler()


@app.on_event("startup")
async def on_startup():
    init_db()

    llm_service = LLMService(db_session=Session(db_engine))

    background_scheduler.add_job(
        llm_service.init_ollama, "date", run_date=datetime.now()
    )

    background_scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    print("FastApi: shutdown")
    background_scheduler.shutdown()
