"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import logger
from app.core.dependencies import get_current_active_user  # Import dependency
from app.db import crud
from app.db.session import get_db
from app.schemas import Token, User

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),  # Use OAuth2 form data
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
    elif not user.is_active:
        logger.warning(f"Authentication failed for inactive user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token = security.create_access_token(subject=user.id)
    logger.info(f"Login successful, token generated for user: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")  # Placeholder for logout functionality
async def logout():
    """
    Placeholder for logout. JWT is stateless, so true logout happens client-side
    by discarding the token. Server-side might involve token blocklisting if needed.
    """
    # In a stateless JWT setup, logout is primarily a client-side action
    # (deleting the token). If using refresh tokens or a token blacklist,
    # server-side logic would be added here.
    logger.info("Logout endpoint called (stateless).")
    return {"message": "Logout successful (token should be discarded client-side)"}


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),  # Use dependency
) -> Any:
    """
    Get current logged-in user's details.
    """
    logger.info(f"Fetching details for current user: {current_user.email}")
    return current_user
