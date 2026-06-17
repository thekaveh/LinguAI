from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe.

    Returns a small JSON payload so callers (the frontend admin ping, container
    healthchecks) can confirm the backend is up and serving the v1 API.
    """
    return {"message": "ok"}
