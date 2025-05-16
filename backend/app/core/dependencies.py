from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError  # Import ValidationError for Pydantic v2+
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import logger, settings
from app.db import crud
from app.db.models import User
from app.db.session import get_db
from app.schemas import TokenPayload

# OAuth2PasswordBearer scheme configuration
# tokenUrl points to the endpoint where the client gets the token (e.g., /api/v1/auth/login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current authenticated user based on the JWT token.

    Raises:
        HTTPException 401 (Unauthorized) if token is invalid, expired, or user not found/inactive.
        HTTPException 403 (Forbidden) if token is missing (handled by OAuth2PasswordBearer).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = security.decode_token(token)

    if token_data is None or token_data.sub is None:
        logger.warning("Token decoding failed or subject (sub) missing.")
        raise credentials_exception

    try:
        # Ensure the subject is a valid UUID before querying the database
        user_id = UUID(str(token_data.sub))
    except (ValueError, TypeError):
        logger.warning(f"Invalid user ID format in token subject: {token_data.sub}")
        raise credentials_exception

    user = await crud.user.get(db, user_id=user_id)
    if user is None:
        logger.warning(f"User not found for ID: {user_id}")
        raise credentials_exception

    # Optional: Add checks like user.is_active
    # if not user.is_active:
    #     logger.warning(f"Inactive user attempted access: {user.email}")
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    logger.debug(f"Authenticated user retrieved: {user.email} (ID: {user.id})")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current active authenticated user.
    Builds upon get_current_user by adding an explicit active check.
    """
    if not current_user.is_active:
        logger.warning(
            f"Inactive user attempted access requiring active status: {current_user.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    logger.debug(f"Active user confirmed: {current_user.email}")
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency to get the current active superuser.
    Requires the user to be both active and a superuser.
    """
    if not crud.user.is_superuser(current_user):
        logger.warning(
            f"Non-superuser attempted access requiring superuser role: {current_user.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    logger.debug(f"Superuser access granted: {current_user.email}")
    return current_user


# You can add more dependencies here for specific roles if needed, e.g., get_current_analyst
