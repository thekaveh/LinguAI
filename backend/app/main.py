import logging
from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.models import Info
from fastapi.openapi.utils import get_openapi


logging.basicConfig(
    level=logging.DEBUG,
    filename='/app/logs/backend-app.log',
                    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

app = FastAPI()

app.include_router(v1_router)