from langserve import add_routes
from fastapi import APIRouter, HTTPException

from app.services.llm_service import LLMService

router = APIRouter()

@router.get("/llm/list")
async def list():
    try:
        result = LLMService.list_models()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

for model in LLMService.list_models():
	add_routes(
		app=router
		, path=f"/llm/chat/{model}"
		, enabled_endpoints=["stream"]
		, runnable=LLMService.get_runnable(model=model)
	)