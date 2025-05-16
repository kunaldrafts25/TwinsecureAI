from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.password import get_password_hash, verify_password
from app.db.models import User
from app.schemas.user_schema import UserCreate, UserUpdate


class CRUDUser:
    """CRUD operations for User model."""

    async def get(self, db: AsyncSession, user_id: Union[UUID, str]) -> Optional[User]:
        """Get a single user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get a single user by email."""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get multiple users with pagination."""
        stmt = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(obj_in.password)
        # Create user instance without password
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
            role=obj_in.role,
        )
        db.add(db_obj)
        await db.commit()  # Commit to get the ID generated
        await db.refresh(db_obj)  # Refresh to load relationships or defaults
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, dict]
    ) -> User:
        """Update an existing user."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(
                exclude_unset=True
            )  # Use model_dump for Pydantic v2+

        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]  # Don't store plain password
        else:
            # Ensure password/hashed_password isn't accidentally set to None if not provided
            update_data.pop("password", None)
            update_data.pop("hashed_password", None)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not user.is_active:  # Optional: check if user is active
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def is_superuser(self, user: User) -> bool:
        """Check if a user is a superuser."""
        return user.is_superuser


# Instantiate the CRUD class
user = CRUDUser()
