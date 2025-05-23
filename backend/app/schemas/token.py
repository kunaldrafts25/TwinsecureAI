"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

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
