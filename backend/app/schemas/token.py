from typing import Optional

from pydantic import UUID4, BaseModel


class Token(BaseModel):
    """
    Schema for the JWT access token response.
    """

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Schema for the data encoded within the JWT token.
    """

    sub: Optional[UUID4] = None  # Subject (user ID)
