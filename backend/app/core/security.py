from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings, logger
from app.schemas import TokenPayload

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM

def create_access_token(subject: Union[str, UUID, Any], expires_delta: Optional[timedelta] = None) -> str:
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
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)} # Ensure subject is a string
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Created access token for subject {subject} expiring at {expire}")
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.

    Args:
        plain_password: The plain text password.
        hashed_password: The hashed password from the database.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain password using the configured context.

    Args:
        password: The plain text password.

    Returns:
        The hashed password string.
    """
    return pwd_context.hash(password)

def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decodes a JWT token and returns the payload.

    Args:
        token: The encoded JWT token string.

    Returns:
        The TokenPayload schema instance or None if decoding fails or token is invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        # Explicitly create TokenPayload to handle potential missing 'sub' or validate type
        token_data = TokenPayload(sub=payload.get("sub"))
        # Optional: Add more validation here, e.g., check 'exp' claim validity more strictly if needed
        logger.debug(f"Token decoded successfully for subject: {token_data.sub}")
        return token_data
    except JWTError as e:
        logger.warning(f"JWT Error decoding token: {e}")
        return None
    except Exception as e: # Catch potential Pydantic validation errors or other issues
        logger.error(f"Error processing token payload: {e}")
        return None