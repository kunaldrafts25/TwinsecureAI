"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import logger, settings

# Create an asynchronous engine instance.
# pool_pre_ping=True checks connections for liveness before handing them out.
# echo=True logs SQL queries (useful for debugging, disable in production)
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.ENVIRONMENT == "development",  # Log SQL only in dev
)

# Create an asynchronous session factory.
# expire_on_commit=False prevents attributes from being expired after commit,
# which is useful in async contexts.
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

logger.info(f"Async database engine created for URL: {settings.DATABASE_URL}")


# Dependency to get a DB session
async def get_db() -> AsyncSession:
    """
    FastAPI dependency that provides an async database session.
    Ensures the session is closed after the request is finished.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Commit changes if no exceptions occurred
        except Exception as e:
            await session.rollback()  # Rollback changes on error
            logger.error(f"Database transaction rolled back due to error: {e}")
            raise  # Re-raise the exception
        finally:
            await session.close()  # Ensure session is closed


# --- Initial DB Setup (Optional - often handled by Alembic) ---
# This part is more for initial setup or simple cases.
# Production environments typically use Alembic for migrations.

from app.db.__init__ import init_db  # Import the initialization function
from app.db.base import Base  # Import Base AFTER defining engine and SessionLocal


async def initialize_database():
    """
    Initializes the database: creates tables and the first superuser.
    Should ideally be run once on startup or via a CLI command.
    """
    logger.info("Initializing database...")
    try:
        async with engine.begin() as conn:
            # This creates tables based on SQLAlchemy models (Base.metadata)
            # It won't modify existing tables, making it safe to run multiple times.
            # However, Alembic is preferred for managing schema changes.
            # await conn.run_sync(Base.metadata.create_all)
            logger.warning(
                "Skipping Base.metadata.create_all(). Use Alembic migrations ('alembic upgrade head') instead."
            )

        # Create the first superuser if specified in settings
        async with AsyncSessionLocal() as session:
            await init_db(session)
            logger.info("Database initialization check complete.")

    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        # Depending on the error, you might want to exit the application
        # raise SystemExit(f"Could not initialize database: {e}")


# Note: The actual call to initialize_database() would typically happen
# in main.py's startup event or a separate management script.
# For simplicity with Alembic, we often rely on running `alembic upgrade head`
# before starting the application server.
