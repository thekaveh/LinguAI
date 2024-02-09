from fastapi import APIRouter, Body, HTTPException

from app.services.joke_service import JokeService

router = APIRouter()

@router.post("/joke")
async def joke(topic: str = Body(..., embed=True), llm_type: str = Body(..., embed=True)):
    service = JokeService()
    
    try:
        result = service.process(topic, llm_type)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
