"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

#!/usr/bin/env python
"""
Database initialization script.
This script initializes the database with required tables and initial data.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import logger, settings
from app.db.base import Base
from app.db.config import get_database_url
from app.db.crud.crud_user import create_user
from app.db.session import get_db
from app.schemas.user import UserCreate


async def create_tables():
    """Create database tables."""
    try:
        # Create async engine
        engine = create_async_engine(
            get_database_url(),
            echo=True,
        )
        
        # Create tables
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
        
        # Close engine
        await engine.dispose()
        
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False


async def create_initial_data():
    """Create initial data in the database."""
    try:
        # Create first superuser if configured
        if settings.FIRST_SUPERUSER and settings.FIRST_SUPERUSER_PASSWORD:
            logger.info(f"Creating first superuser: {settings.FIRST_SUPERUSER}")
            
            # Get database session
            async for db in get_db():
                # Check if user already exists
                from app.db.crud.crud_user import get_by_email
                existing_user = await get_by_email(db, email=settings.FIRST_SUPERUSER)
                
                if existing_user:
                    logger.info(f"Superuser {settings.FIRST_SUPERUSER} already exists")
                else:
                    # Create user object
                    user_in = UserCreate(
                        email=settings.FIRST_SUPERUSER,
                        password=settings.FIRST_SUPERUSER_PASSWORD,
                        full_name="Initial Admin",
                        is_superuser=True,
                        role="ADMIN"
                    )
                    
                    # Create user in database
                    await create_user(db, obj_in=user_in)
                    logger.info(f"Superuser {settings.FIRST_SUPERUSER} created successfully")
                
                break
        
        logger.info("Initial data created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
        return False


async def init_db():
    """Initialize the database."""
    # Create tables
    tables_created = await create_tables()
    
    if not tables_created:
        logger.error("Failed to create database tables")
        return False
    
    # Create initial data
    data_created = await create_initial_data()
    
    if not data_created:
        logger.error("Failed to create initial data")
        return False
    
    logger.info("Database initialized successfully")
    return True


if __name__ == "__main__":
    """Run the script directly."""
    logger.info("Initializing database...")
    
    # Run the async function
    success = asyncio.run(init_db())
    
    if success:
        logger.info("Database initialization completed successfully")
        sys.exit(0)
    else:
        logger.error("Database initialization failed")
        sys.exit(1)
