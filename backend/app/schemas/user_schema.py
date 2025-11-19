"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

User schemas for API requests and responses.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.enums import UserRole


class UserBase(BaseModel):
    """Shared properties across all user schemas."""
    
    email: EmailStr | None = None
    is_active: bool | None = True
    is_superuser: bool = False
    full_name: str | None = None
    role: UserRole | None = UserRole.VIEWER  # Default to viewer role


class UserCreate(UserBase):
    """Properties required when creating a user."""
    
    email: EmailStr  # Email is required
    password: str  # Password is required
    role: UserRole = UserRole.VIEWER  # Default to viewer role


class UserUpdate(UserBase):
    """Properties allowed when updating a user."""
    
    password: str | None = None  # Allow password updates


class UserInDBBase(UserBase):
    """Properties stored in DB (includes internal fields)."""
    
    id: UUID
    hashed_password: str
    created_at: datetime
    updated_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    """Properties returned to client (safe for API response)."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)
