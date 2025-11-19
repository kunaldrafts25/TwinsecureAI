"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Database initialization - creates first superuser on startup.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger, settings
from app.core.enums import UserRole
from app.db import crud
from app.schemas.user_schema import UserCreate


async def init_db(db: AsyncSession) -> None:
    """
    Initialize the database by creating the first superuser if it doesn't exist.
    
    This function is called on application startup to ensure there's always
    an admin account available for initial access.
    """
    logger.info("Checking if superuser needs to be created...")
    
    # Check if superuser already exists
    first_superuser_email = getattr(settings, "FIRST_SUPERUSER", None)
    first_superuser_password = getattr(settings, "FIRST_SUPERUSER_PASSWORD", None)

    if not first_superuser_email or not first_superuser_password:
        logger.warning("FIRST_SUPERUSER or FIRST_SUPERUSER_PASSWORD not configured. Skipping superuser creation.")
        return

    user = await crud.user.get_by_email(
        db,
        email=first_superuser_email
    )
    
    if not user:
        logger.info(f"Creating superuser: {first_superuser_email}")
        
        user_in = UserCreate(
            email=first_superuser_email,
            password=first_superuser_password.get_secret_value() if hasattr(first_superuser_password, "get_secret_value") else str(first_superuser_password),
            full_name="System Administrator",
            is_superuser=True,
            is_active=True,
            role=UserRole.ADMIN,
        )
        
        try:
            user = await crud.user.create(db=db, obj_in=user_in)
            logger.info("Superuser created successfully")
        except Exception as e:
            logger.error(f"Error creating superuser: {e}")
            
            # Check if user was created by another process (race condition)
            user = await crud.user.get_by_email(
                db,
                email=first_superuser_email
            )
            
            if user:
                logger.warning("Superuser already existed or was created concurrently")
            else:
                # If still not found, creation truly failed
                raise
    else:
        logger.info("Superuser already exists")
