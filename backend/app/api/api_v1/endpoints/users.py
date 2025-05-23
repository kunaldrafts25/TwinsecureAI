"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_superuser, get_current_active_user
from app.db import crud
from app.db.session import get_db
from app.schemas import User, UserCreate, UserUpdate

# You will need to import necessary schemas and dependencies here later
# from app.schemas.user import User, UserCreate, UserUpdate, UserInDB # Example user schemas
# from app.core.dependencies import get_current_active_user, get_current_active_superuser # Example dependencies
# from app.services.user import create_user, get_user, get_users, update_user, delete_user # Example service functions

# Define the APIRouter for user endpoints
router = APIRouter()

# --- CRITICAL STEP: Make the router available for import ---
# Assign the router instance to a variable named 'users'
users = router


# Add your user-related endpoints here later
# Example placeholder endpoint:
@router.get("/me", response_model=dict)  # Replace dict with your User schema
async def read_users_me(
    # current_user: User = Depends(get_current_active_user) # Example dependency usage
):
    """
    Get current user.
    """
    # return current_user # Example return
    return {"message": "User endpoint placeholder"}  # Placeholder response


@router.get("/", response_model=List[User])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    users = await crud.user.get_multi(db)
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    user = await crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    user = await crud.user.create(db, obj_in=user_in)
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    user = await crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    user = await crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await crud.user.delete(db, user_id=user_id)
    return None


# Add other endpoints like create user, get user by id, etc.
