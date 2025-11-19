"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Database session management and async engine configuration.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import logger, settings

# Create async engine
# pool_pre_ping ensures connections are alive before use
# echo logs SQL queries (only in development)
# SQLite requires special connection args
db_url = settings.database.DATABASE_URL
connect_args = {}

# SQLite-specific configuration
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # SQLite doesn't support pool_size and max_overflow
    engine = create_async_engine(
        db_url,
        echo=settings.ENVIRONMENT == "development",
        connect_args=connect_args,
        pool_pre_ping=False,  # SQLite doesn't need this
    )
else:
    # PostgreSQL configuration
    engine = create_async_engine(
        db_url,
        pool_pre_ping=True,
        echo=settings.ENVIRONMENT == "development",
        pool_size=5,
        max_overflow=10,
    )

# Create async session factory
# expire_on_commit=False prevents attributes from expiring after commit in async
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

logger.info("Async database engine initialized")


async def get_db():
    """
    FastAPI dependency that provides an async database session.
    
    Automatically handles commit/rollback and session cleanup.
    
    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database transaction rolled back: {e}")
            raise
        finally:
            await session.close()


async def initialize_database():
    """
    Initialize database: create tables and first superuser.
    
    This should be called on application startup. For production,
    use Alembic migrations (`alembic upgrade head`) before starting the server.
    """
    from app.db import init_db
    from app.db.base import Base
    
    logger.info("Initializing database...")
    
    try:
        # Uncomment to auto-create tables (not recommended for production)
        # async with engine.begin() as conn:
        #     await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Using Alembic for migrations. Run: alembic upgrade head")
        
        # Create first superuser if needed
        async with AsyncSessionLocal() as session:
            await init_db(session)
        
        logger.info("Database initialization complete")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise
