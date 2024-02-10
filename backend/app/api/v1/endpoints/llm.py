from fastapi import APIRouter, Body, HTTPException

from app.services.llm_service import LlmService

router = APIRouter()

@router.get("/llms/get")
async def get_llms():
    service = LlmService()
    
    try:
        result = service.list_llms()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
