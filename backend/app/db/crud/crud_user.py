"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

CRUD operations for User model.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.password import get_password_hash, verify_password
from app.db.models import User
from app.schemas.user_schema import UserCreate, UserUpdate


class CRUDUser:
    """CRUD operations for User model"""
    
    async def get(
        self,
        db: AsyncSession,
        user_id: UUID | str
    ) -> User | None:
        """Get a single user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> User | None:
        """Get a single user by email"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """Get multiple users with pagination"""
        stmt = (
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: UserCreate
    ) -> User:
        """Create a new user with hashed password"""
        hashed_password = get_password_hash(obj_in.password)
        
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
            role=obj_in.role,
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: UserUpdate | dict
    ) -> User:
        """Update an existing user"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Handle password update
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]
        else:
            update_data.pop("password", None)
            update_data.pop("hashed_password", None)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(
        self,
        db: AsyncSession,
        *,
        user_id: UUID | str
    ) -> User | None:
        """Delete a user by ID"""
        db_obj = await self.get(db, user_id=user_id)
        
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return db_obj
        
        return None
    
    async def authenticate(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str
    ) -> User | None:
        """Authenticate a user by email and password"""
        user = await self.get_by_email(db, email=email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def is_superuser(self, user: User) -> bool:
        """Check if a user is a superuser"""
        return user.is_superuser


# Instantiate the CRUD class
user = CRUDUser()
