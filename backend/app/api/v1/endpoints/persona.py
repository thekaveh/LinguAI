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
    """
    Retrieve all personas.

    Returns:
        List[Persona]: A list of all personas.
    
    Raises:
        HTTPException: If there is an error retrieving the personas.
    """
    try:
        return service.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/personas/by_id/{id}", response_model=None)
def get_by_id(id: int, service: PersonaService = Depends(_get_service)):
    """
    Retrieve a persona by its ID.

    Args:
        id (int): The ID of the persona to retrieve.
        service (PersonaService, optional): The PersonaService instance to use. Defaults to Depends(_get_service).

    Returns:
        The persona with the specified ID.

    Raises:
        HTTPException: If the persona with the specified ID is not found.
    """
    persona = service.get_by_id(id)

    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found!")

    return persona


@log_decorator
@router.get("/personas/by_name/{name}", response_model=None)
def get_by_name(name: str, service: PersonaService = Depends(_get_service)):
    """
    Retrieve a persona by name.

    Args:
        name (str): The name of the persona.
        service (PersonaService, optional): The PersonaService instance. Defaults to Depends(_get_service).

    Returns:
        The persona with the specified name.

    Raises:
        HTTPException: If the persona is not found.
    """
    persona = service.get_by_name(name)

    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found!")

    return persona


@router.post("/personas/")
def create(persona: Persona, service: PersonaService = Depends(_get_service)):
    """
    Create a new persona.

    Args:
        persona (Persona): The persona object containing the details of the persona to be created.
        service (PersonaService, optional): The PersonaService instance used to create the persona. Defaults to Depends(_get_service).

    Returns:
        Any: The created persona.

    Raises:
        HTTPException: If an error occurs while creating the persona.
    """
    try:
        return service.create(persona)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.put("/personas/{id}")
def update_persona(
    id: int, persona: Persona, service: PersonaService = Depends(_get_service)
):
    """
    Update a persona with the given ID.

    Args:
        id (int): The ID of the persona to update.
        persona (Persona): The updated persona data.
        service (PersonaService, optional): The PersonaService instance to use for updating the persona. Defaults to Depends(_get_service).

    Returns:
        Updated persona: The updated persona object.

    Raises:
        HTTPException: If the persona with the given ID is not found.
    """
    updated = service.update(id, persona)

    if updated is None:
        raise HTTPException(status_code=404, detail="Persona not found!")

    return updated


@log_decorator
@router.delete("/personas/{id}", response_model=None)
def delete_persona(id: int, service: PersonaService = Depends(_get_service)):
    """
    Delete a persona by ID.

    Args:
        id (int): The ID of the persona to delete.
        service (PersonaService, optional): The PersonaService instance used to delete the persona. Defaults to Depends(_get_service).

    Returns:
        dict: A dictionary with a success message if the persona is deleted successfully.

    Raises:
        HTTPException: If an error occurs while deleting the persona.
    """
    try:
        service.delete(id)
        return {"message": "Persona deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
