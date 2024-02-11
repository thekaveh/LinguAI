# import langserve

from fastapi import FastAPI
from app.api.v1.router import router as v1_router

# from .services.llm_service import LlmService

app = FastAPI()

app.include_router(v1_router)

# langserve.add_routes(
#     app
#     , LlmService().get_llm(llm_name="ollama/llama:latest")
#     , path="/v1/llm/ollama"
# )