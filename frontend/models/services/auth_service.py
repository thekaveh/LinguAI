from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import httpx

from models.schemas.authentication import AuthenticationRequest


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    username: Optional[str] = None
    user_type: Optional[str] = None
    token: Optional[str] = None
    message: str = ""


class AuthService:
    """Async gateway to the backend's authentication endpoint."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def authenticate(self, req: AuthenticationRequest) -> AuthResult:
        try:
            r = await self._http.post("/users/authenticate", json=req.model_dump())
            r.raise_for_status()
            data = r.json()
            ok = bool(data.get("status", False))
            username = data.get("username")
            # Backend doesn't issue a real token; we use the username as a stand-in so
            # the Authorization header gets populated. Future endpoints can read it.
            # TODO(post-phase-7): once the backend issues real tokens, swap this.
            token = username if (ok and username) else None
            return AuthResult(
                ok=ok,
                username=username,
                user_type=None,  # backend doesn't return this today; fetch separately via user_service if needed
                token=token,
                message=str(data.get("message", "")),
            )
        except httpx.HTTPStatusError as e:
            return AuthResult(ok=False, message=f"auth failed ({e.response.status_code})")
        except httpx.HTTPError as e:
            return AuthResult(ok=False, message=f"network error: {e}")

    async def logout(self) -> None:
        # Backend has no /logout endpoint; logout is client-side only (clear token + storage).
        return None
