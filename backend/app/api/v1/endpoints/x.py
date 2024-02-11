from fastapi import APIRouter, Body, HTTPException

from app.services.llm_service import LlmService

from importlib import metadata
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response
from langchain_core.runnables import RunnableLambda
from sse_starlette import EventSourceResponse

from langserve import APIHandler

router = APIRouter()

# @router.get("/llm/list")
# async def list_llms():
#     service = LlmService()
    
#     try:
#         result = service.list_llms()
#         return {"result": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

async def _get_api_handler() -> APIHandler:
    """Prepare a RunnableLambda."""
    return APIHandler(LlmService().get_llm(llm_name="ollama/llama2"), path="/llm/ollama")

@router.post("/llm/ollama/stream")
async def ollama_stream(
    request: Request
    , runnable: Annotated[APIHandler, Depends(_get_api_handler)]
) -> EventSourceResponse:
    """Handle stream request."""
    # The API Handler validates the parts of the request
    # that are used by the runnnable (e.g., input, config fields)
    return await runnable.stream(request)