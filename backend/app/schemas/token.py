"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

JWT token schemas.
"""

from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for the JWT access token response."""
    
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for the data encoded within the JWT token."""
    
    sub: UUID | None = None  # Subject (user ID)
