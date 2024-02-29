from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.models import Info
from fastapi.openapi.utils import get_openapi

app = FastAPI()

app.include_router(v1_router)


""" # Custom route for Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Documentation")

# OpenAPI JSON endpoint
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return app.openapi() """