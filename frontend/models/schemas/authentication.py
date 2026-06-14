from typing import Optional
from pydantic import BaseModel

from .user import User


class AuthenticationRequest(BaseModel):
    username: str
    password: str


class AuthenticationResponse(BaseModel):
    status: bool
    message: str
    username: Optional[str] = None

    @staticmethod
    def failure(message: str):
        return AuthenticationResponse(status=False, message=message)

    @staticmethod
    def success(username: str):
        return AuthenticationResponse(
            status=True, message="Login successful", username=username
        )
