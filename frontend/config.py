import os

class Config:
    BACKEND_ENDPOINT = os.environ.get("BACKEND_ENDPOINT", "http://backend:8001")