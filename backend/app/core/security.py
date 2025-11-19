"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

JWT token creation and validation utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import logger, settings
from app.core.password import get_password_hash, verify_password
from app.schemas import TokenPayload

# JWT settings from nested config
ALGORITHM = settings.security.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.security.REFRESH_TOKEN_EXPIRE_DAYS
SECRET_KEY = settings.security.SECRET_KEY.get_secret_value()


def create_access_token(
    subject: str | UUID | Any,
    expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The token subject (typically user ID)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.debug(f"Created access token for subject {subject} expiring at {expire}")
    return encoded_jwt


def decode_token(token: str) -> TokenPayload | None:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The encoded JWT token string
    
    Returns:
        TokenPayload instance or None if invalid/expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(sub=payload.get("sub"))
        
        logger.debug(f"Token decoded successfully for subject: {token_data.sub}")
        return token_data
        
    except JWTError as e:
        logger.warning(f"JWT Error decoding token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error processing token payload: {e}")
        return None


# Re-export password functions for convenience
__all__ = [
    "create_access_token",
    "decode_token",
    "get_password_hash",
    "verify_password"
]
