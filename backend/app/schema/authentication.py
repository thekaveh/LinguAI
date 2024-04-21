from typing import Optional
from pydantic import BaseModel

from .user import User


class AuthenticationRequest(BaseModel):
    username: str
    password: str


class AuthenticationResponse(BaseModel):
    """
    Represents the response object for authentication.

    Attributes:
        status (bool): The status of the authentication request.
        message (str): The message associated with the authentication request.
        username (Optional[str], optional): The username associated with the authentication request. Defaults to None.
    """

    status: bool
    message: str
    username: Optional[str] = None

    @staticmethod
    def failure(message: str):
        """
        Creates an AuthenticationResponse object for a failed authentication request.

        Args:
            message (str): The message associated with the failed authentication request.

        Returns:
            AuthenticationResponse: The AuthenticationResponse object representing the failed authentication request.
        """
        return AuthenticationResponse(status=False, message=message)

    @staticmethod
    def success(username: str):
        """
        Creates an AuthenticationResponse object for a successful authentication request.

        Args:
            username (str): The username associated with the successful authentication request.

        Returns:
            AuthenticationResponse: The AuthenticationResponse object representing the successful authentication request.
        """
        return AuthenticationResponse(
            status=True, message="Login successful", username=username
        )
