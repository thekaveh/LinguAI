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