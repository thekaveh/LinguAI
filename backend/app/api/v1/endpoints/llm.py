from langserve import add_routes
from fastapi import APIRouter, HTTPException

from app.services.llm_service import LLMService

router = APIRouter()

@router.get("/llm/list")
async def list_llms():
    try:
        result = LLMService().list_llms()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

for llm in LLMService().list_llms():
	add_routes(
		app=router
		, path=f"/llm/chat/{llm}"
		, enabled_endpoints=["stream"]
		, runnable=LLMService().get_llm(name=llm)
	)
