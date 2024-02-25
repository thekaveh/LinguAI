import logging
from fastapi import FastAPI
from app.api.v1.router import router as v1_router

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

app.include_router(v1_router)