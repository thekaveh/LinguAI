from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends

from app.utils.logger import log_decorator
from app.services.llm_service import LLMService
from app.services.dependency.db_service import get_db_session

router = APIRouter()


def _get_service(db_session: Session = Depends(get_db_session)) -> LLMService:
    return LLMService(db_session=db_session)


@log_decorator
@router.get("/llms/all/")
def get_all(service: LLMService = Depends(_get_service)):
    """
    Retrieve all LLMs.

    Returns:
        List[LLM]: A list of all LLMs.

    Raises:
        HTTPException: If there is an error retrieving the LLMs.
    """
    try:
        return service.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/llms/embeddings/")
def get_embeddings(service: LLMService = Depends(_get_service)):
    """
    Retrieve ordered list of LLMs that support generating embeddings.

    This endpoint returns the embeddings for the LLMs. It calls the `get_embeddings` method of the `LLMService` class.

    Returns:
        The ordered list of LLMs that support generating embeddings.

    Raises:
        HTTPException: If there is an error retrieving the embeddings.
    """
    try:
        return service.get_embeddings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/llms/content/")
def get_content(service: LLMService = Depends(_get_service)):
    """
    Retrieve ordered list of LLMs that support generating content.

    Args:
        service (LLMService): The LLM service instance.

    Returns:
        The ordered list of LLMs that support generating content.

    Raises:
        HTTPException: If there is an error retrieving the content.
    """
    try:
        return service.get_content()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/llms/structured_content/")
def get_structured_content(service: LLMService = Depends(_get_service)):
    """
    Retrieve ordered list of LLMs that support generating structured content.

    Args:
        service (LLMService): The LLM service instance.

    Returns:
        The ordered list of LLMs that support generating structured content.

    Raises:
        HTTPException: If there is an error retrieving the content.
    """
    try:
        return service.get_structured_content()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/llms/vision/")
def get_vision(service: LLMService = Depends(_get_service)):
    """
    Retrieve ordered list of LLMs that support vision.

    Parameters:
    - service: An instance of the LLMService class.

    Returns:
    - The ordered list of LLMs that support vision.

    Raises:
    - HTTPException: If an error occurs while retrieving the vision data.
    """
    try:
        return service.get_vision()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@log_decorator
@router.get("/llms/by_name/{name}", response_model=None)
def get_by_name(name: str, service: LLMService = Depends(_get_service)):
    """
    Retrieve an LLM by its name.

    Args:
        name (str): The name of the LLM to retrieve.
        service (LLMService, optional): The LLM service dependency. Defaults to _get_service.

    Returns:
        LLM: The retrieved LLM.

    Raises:
        HTTPException: If the LLM is not found.
    """
    llm = service.get_by_name(name)

    if llm is None:
        raise HTTPException(status_code=404, detail="LLM not found!")

    return llm


@log_decorator
@router.get("/llms/by_id/{id}", response_model=None)
def get_by_id(id: int, service: LLMService = Depends(_get_service)):
    """
    Retrieve an LLM by its ID.

    Args:
        id (int): The ID of the LLM to retrieve.
        service (LLMService, optional): The LLM service dependency. Defaults to _get_service.

    Returns:
        LLM: The retrieved LLM object.

    Raises:
        HTTPException: If the LLM with the specified ID is not found.
    """
    llm = service.get_by_id(id)

    if llm is None:
        raise HTTPException(status_code=404, detail="LLM not found!")

    return llm
