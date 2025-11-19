#!/usr/bin/env python
"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Database initialization script.
Creates all database tables and initial superuser account.

Usage:
    python scripts/init_db.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import SecretStr
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import logger, settings
from app.db.base import Base
from app.db.config import get_database_url
from app.db.crud.crud_user import create_user, get_by_email
from app.db.session import get_db
from app.schemas.user import UserCreate


async def create_tables() -> bool:
    """Create all database tables from SQLAlchemy models."""
    try:
        # Create async engine with echo for debugging
        engine = create_async_engine(
            get_database_url(),
            echo=True,
        )
        
        # Create all tables
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
        
        # Close engine
        await engine.dispose()
        
        logger.info("✓ Database tables created successfully")
        return True
    
    except Exception as e:
        logger.error(f"✗ Error creating database tables: {e}", exc_info=True)
        return False


async def create_initial_superuser() -> bool:
    """Create initial superuser if configured in settings."""
    try:
        # Check if superuser credentials are configured
        if not settings.FIRST_SUPERUSER or not settings.FIRST_SUPERUSER_PASSWORD:
            logger.warning(
                "FIRST_SUPERUSER or FIRST_SUPERUSER_PASSWORD not set. "
                "Skipping superuser creation."
            )
            return True
        
        logger.info(f"Creating first superuser: {settings.FIRST_SUPERUSER}")
        
        # Get database session
        async for db in get_db():
            # Check if user already exists
            existing_user = await get_by_email(db, email=settings.FIRST_SUPERUSER)
            
            if existing_user:
                logger.info(f"✓ Superuser {settings.FIRST_SUPERUSER} already exists")
            else:
                # Extract password (handle SecretStr)
                password = settings.FIRST_SUPERUSER_PASSWORD
                
                if isinstance(password, SecretStr):
                    password = password.get_secret_value()
                
                # Create user object
                user_in = UserCreate(
                    email=settings.FIRST_SUPERUSER,
                    password=password,
                    full_name="System Administrator",
                    is_superuser=True,
                    role="ADMIN"
                )
                
                # Create user in database
                await create_user(db, obj_in=user_in)
                logger.info(f"✓ Superuser {settings.FIRST_SUPERUSER} created successfully")
            
            break  # Only need first session
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Error creating initial superuser: {e}", exc_info=True)
        return False


async def init_db() -> bool:
    """
    Initialize the database.
    Creates tables and initial data.
    """
    print("\n" + "="*60)
    print("TwinSecure Database Initialization")
    print("="*60 + "\n")
    
    # Step 1: Create tables
    print("Step 1: Creating database tables...")
    tables_created = await create_tables()
    
    if not tables_created:
        print("\n✗ Failed to create database tables")
        return False
    
    # Step 2: Create initial superuser
    print("\nStep 2: Creating initial superuser...")
    superuser_created = await create_initial_superuser()
    
    if not superuser_created:
        print("\n✗ Failed to create initial superuser")
        return False
    
    print("\n" + "="*60)
    print("✓ Database initialization completed successfully!")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    """Run the script directly."""
    logger.info("Starting database initialization...")
    
    # Run the async function
    success = asyncio.run(init_db())
    
    if success:
        logger.info("Database initialization completed successfully")
        sys.exit(0)
    else:
        logger.error("Database initialization failed")
        sys.exit(1)
