from pydantic import BaseModel

class PasswordChange(BaseModel):
    """
    Represents a password change request.

    Attributes:
        current_password (str): The current password of the user.
        new_password (str): The new password to be set for the user.
    """
    current_password: str
    new_password: str