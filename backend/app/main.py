from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import Config
from app.api.v1.router import router as v1_router
from app.services.dependency.db_service import init_db
from app.utils.logger_config import setup_global_logging

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