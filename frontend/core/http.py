from __future__ import annotations
from typing import Optional

import httpx

from core.config import AppConfig


def build_http_client(cfg: AppConfig) -> httpx.AsyncClient:
    """Construct the shared httpx.AsyncClient.

    Backend mounts its v1 router under /v1; append unconditionally so service
    call sites stay clean (e.g. http.get("/users/list") → backend /v1/users/list).
    Auth header is injected per-request by UserSessionVM.
    """
    base = cfg.backend_endpoint.rstrip("/") + "/v1"
    return httpx.AsyncClient(
        base_url=base,
        timeout=httpx.Timeout(
            connect=cfg.http_connect_timeout_s,
            read=cfg.http_read_timeout_s,
            write=cfg.http_read_timeout_s,
            pool=cfg.http_read_timeout_s,
        ),
        transport=httpx.AsyncHTTPTransport(retries=2),
    )


def set_bearer_token(client: httpx.AsyncClient, token: Optional[str]) -> None:
    """Set or clear the Authorization header on the shared client.

    TODO(security): the token is currently just the username because the backend
    doesn't issue real auth tokens yet. Replace with JWT / opaque token once
    backend supports it; current behaviour is impersonation-vulnerable.
    """
    if token:
        client.headers["Authorization"] = f"Bearer {token}"
    else:
        client.headers.pop("Authorization", None)
