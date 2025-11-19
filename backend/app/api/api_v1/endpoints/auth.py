"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import logger
from app.core.dependencies import get_current_active_user, oauth2_scheme
from app.core.token_blacklist import add_to_blacklist
from app.db import crud
from app.db.session import get_db
from app.schemas import Token, User

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Uses username (which is email in our case) and password from form data.
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    
    if not user:
        logger.warning(f"Authentication failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning(f"Inactive user attempted login: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    access_token = security.create_access_token(subject=user.id)
    logger.info(f"Login successful for user: {user.email}")
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """
    Logout endpoint that blacklists the current JWT token.
    Invalidates the token server-side, preventing reuse before expiration.
    """
    logger.info(f"Logout requested for user: {current_user.email}")
    
    success = await add_to_blacklist(token)
    
    if not success:
        logger.warning(f"Failed to blacklist token for user: {current_user.email}")
    
    return {
        "message": "Logout successful. Token has been invalidated.",
        "success": True
    }


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current logged-in user's details."""
    logger.info(f"Fetching details for current user: {current_user.email}")
    return current_user
