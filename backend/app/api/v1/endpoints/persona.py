from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends

from app.models.persona import Persona
from app.utils.logger import log_decorator
from app.services.persona_service import PersonaService
from app.services.dependency.db_service import get_db_session

router = APIRouter()


def _get_service(db_session: Session = Depends(get_db_session)) -> PersonaService:
    return PersonaService(db_session=db_session)


@log_decorator
@router.get("/personas/")
def get_all(service: PersonaService = Depends(_get_service)):
    try:
        return service.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/personas/by_id/{id}", response_model=None)
def get_by_id(id: int, service: PersonaService = Depends(_get_service)):
    persona = service.get_by_id(id)

    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found!")

    return persona


@log_decorator
@router.get("/personas/by_name/{name}", response_model=None)
def get_by_name(name: str, service: PersonaService = Depends(_get_service)):
    persona = service.get_by_name(name)

    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found!")

    return persona


@router.post("/personas/")
def create(persona: Persona, service: PersonaService = Depends(_get_service)):
    try:
        return service.create(persona)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.put("/personas/{id}")
def update(id: int, persona: Persona, service: PersonaService = Depends(_get_service)):
    updated = service.update(id, persona)

    if updated is None:
        raise HTTPException(status_code=404, detail="Persona not found!")

    return updated


@log_decorator
@router.delete("/personas/{id}", response_model=None)
def delete(id: int, service: PersonaService = Depends(_get_service)):
    try:
        service.delete(id)
        return {"message": "Persona deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
