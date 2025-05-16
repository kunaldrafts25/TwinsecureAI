"""
User schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr

from app.core.enums import UserRole


# --- Base Schemas ---
# Properties shared by all user-related schemas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.ADMIN  # Default role for superuser


# Properties required when creating a user
class UserCreate(UserBase):
    email: EmailStr  # Email is required on creation
    password: str  # Password is required on creation


# Properties required when updating a user
class UserUpdate(UserBase):
    password: Optional[str] = None  # Allow password updates


# --- Database Interaction Schemas ---
# Properties stored in DB but not always returned to API (like hashed_password)
class UserInDBBase(UserBase):
    id: UUID4
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enable ORM mode (SQLAlchemy model -> Pydantic schema)


# --- API Response Schema ---
# Properties to return to the client (omits password)
class User(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enable ORM mode
