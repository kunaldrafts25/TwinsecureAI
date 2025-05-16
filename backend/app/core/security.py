from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import logger, settings
from app.core.password import get_password_hash, verify_password
from app.schemas import TokenPayload

# JWT settings
ALGORITHM = settings.SECURITY__ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.SECURITY__ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.SECURITY__REFRESH_TOKEN_EXPIRE_DAYS
SECRET_KEY = settings.SECURITY__SECRET_KEY.get_secret_value()


def create_access_token(
    subject: Union[str, UUID, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a JWT access token.

    Args:
        subject: The subject of the token (typically user ID).
        expires_delta: Optional timedelta for token expiry. Defaults to setting.

    Returns:
        The encoded JWT token string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.SECURITY__ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}  # Ensure subject is a string
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Created access token for subject {subject} expiring at {expire}")
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decodes a JWT token and returns the payload.

    Args:
        token: The encoded JWT token string.

    Returns:
        The TokenPayload schema instance or None if decoding fails or token is invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Explicitly create TokenPayload to handle potential missing 'sub' or validate type
        token_data = TokenPayload(sub=payload.get("sub"))
        # Optional: Add more validation here, e.g., check 'exp' claim validity more strictly if needed
        logger.debug(f"Token decoded successfully for subject: {token_data.sub}")
        return token_data
    except JWTError as e:
        logger.warning(f"JWT Error decoding token: {e}")
        return None
    except Exception as e:  # Catch potential Pydantic validation errors or other issues
        logger.error(f"Error processing token payload: {e}")
        return None
