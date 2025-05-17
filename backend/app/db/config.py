"""
Database configuration module.
This module provides configuration for database connections.
"""

import os
from typing import Dict, Optional

from app.core.config import logger, settings


def get_database_url() -> str:
    """
    Get the database URL based on environment variables.
    
    Returns:
        str: The database URL for SQLAlchemy
    """
    # Check if DATABASE_URL is directly provided
    if hasattr(settings, "DATABASE_URL") and settings.DATABASE_URL:
        logger.info(f"Using provided DATABASE_URL: {settings.DATABASE_URL}")
        return settings.DATABASE_URL
    
    # Otherwise, build from components
    user = settings.POSTGRES_USER
    password = settings.POSTGRES_PASSWORD
    server = settings.POSTGRES_SERVER
    port = settings.POSTGRES_PORT
    db = settings.POSTGRES_DB
    
    # Log the database connection info (without password)
    logger.info(f"Connecting to database: {user}@{server}:{port}/{db}")
    
    # Build the connection URL
    return f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}"


def get_database_config() -> Dict[str, str]:
    """
    Get database configuration as a dictionary.
    
    Returns:
        Dict[str, str]: Database configuration
    """
    return {
        "user": settings.POSTGRES_USER,
        "password": settings.POSTGRES_PASSWORD,
        "host": settings.POSTGRES_SERVER,
        "port": str(settings.POSTGRES_PORT),
        "database": settings.POSTGRES_DB,
    }


def get_test_database_url() -> str:
    """
    Get the test database URL.
    
    Returns:
        str: The test database URL
    """
    # For testing, we can use either a test PostgreSQL database or SQLite
    test_db = os.environ.get("TEST_DB", "sqlite")
    
    if test_db.lower() == "postgres":
        # Use PostgreSQL for testing
        test_host = os.environ.get("TEST_PG_HOST", "localhost")
        test_port = os.environ.get("TEST_PG_PORT", "5432")
        test_user = os.environ.get("TEST_PG_USER", "postgres")
        test_password = os.environ.get("TEST_PG_PASSWORD", "postgres")
        test_db_name = os.environ.get("TEST_PG_DB", "test_twinsecure")
        
        return f"postgresql+asyncpg://{test_user}:{test_password}@{test_host}:{test_port}/{test_db_name}"
    else:
        # Use SQLite for testing (in-memory or file-based)
        return "sqlite+aiosqlite:///./test.db"
