from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.data_access.session import get_db
from app.utils.logger import log_decorator
from app.services.persona_service import PersonaService
from app.schema.persona import (
    PersonaCreate,
    PersonaUpdate,
    Persona,
    PersonaSearch,
)

router = APIRouter()


@log_decorator
@router.post("/personas/", response_model=Persona)
def create(create: PersonaCreate, db: Session = Depends(get_db)):
    service = PersonaService(db)
    return service.create(create)


@log_decorator
@router.get("/personas/{id}", response_model=Persona)
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = PersonaService(db)
    persona = service.get_by_id(id)

    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    return persona


@log_decorator
@router.get("/personas/", response_model=list[Persona])
def get_all(db: Session = Depends(get_db)):
    service = PersonaService(db)
    return service.get_all()


@log_decorator
@router.post("/personas/search", response_model=Persona)
def get_by_criteria(criteria: PersonaSearch, db: Session = Depends(get_db)):
    service = PersonaService(db)
    persona = service.get_by_criteria(criteria)

    if persona is None:
        raise HTTPException(
            status_code=404, detail="Persona not found based on search criteria"
        )

    return persona


@log_decorator
@router.put("/personas/{id}", response_model=Persona)
def update(id: int, update: PersonaUpdate, db: Session = Depends(get_db)):
    service = PersonaService(db)
    updated = service.update(id, update)

    if updated is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    return updated


@log_decorator
@router.delete("/personas/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = PersonaService(db)
        service.delete(id)

        return {"message": "Persona deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
