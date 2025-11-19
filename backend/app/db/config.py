"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Database configuration helpers.
"""

import os
from urllib.parse import quote_plus

from pydantic import SecretStr

from app.core.config import logger, settings


def get_database_url() -> str:
    """
    Get the database URL for SQLAlchemy connections.
    
    First checks for direct DATABASE_URL, otherwise uses DATABASE_TYPE setting.
    Defaults to SQLite if not specified.
    """
    # Check if DATABASE_URL is directly provided
    if hasattr(settings.database, "DATABASE_URL") and settings.database.DATABASE_URL:
        return settings.database.DATABASE_URL
    
    # Use the DATABASE_TYPE from settings (defaults to "sqlite")
    db_type = settings.database.DATABASE_TYPE.lower() if hasattr(settings.database, "DATABASE_TYPE") else "sqlite"
    
    if db_type == "postgres":
        # Build PostgreSQL connection from components
        if not settings.database.POSTGRES_PASSWORD:
            raise ValueError("POSTGRES_PASSWORD is required when using PostgreSQL")
        
        user = settings.database.POSTGRES_USER
        password = settings.database.POSTGRES_PASSWORD
        
        # Handle SecretStr type
        if isinstance(password, SecretStr):
            password = password.get_secret_value()
        
        server = settings.database.POSTGRES_SERVER
        port = settings.database.POSTGRES_PORT
        db = settings.database.POSTGRES_DB
        
        # URL encode password for special characters
        encoded_password = quote_plus(password)
        
        logger.info(f"Connecting to PostgreSQL: {user}@{server}:{port}/{db}")
        return f"postgresql+asyncpg://{user}:{encoded_password}@{server}:{port}/{db}"
    
    # Default to SQLite
    db_path = settings.database.SQLITE_DB_PATH if hasattr(settings.database, "SQLITE_DB_PATH") else "./twinsecure.db"
    logger.info(f"Connecting to SQLite database: {db_path}")
    return f"sqlite+aiosqlite:///{db_path}"


def get_database_config() -> dict[str, str]:
    """
    Get database configuration as a dictionary.
    
    Useful for tools that need separate connection parameters.
    """
    password = settings.database.POSTGRES_PASSWORD
    
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    
    return {
        "user": settings.database.POSTGRES_USER,
        "password": password,
        "host": settings.database.POSTGRES_SERVER,
        "port": str(settings.database.POSTGRES_PORT),
        "database": settings.database.POSTGRES_DB,
    }


def get_test_database_url() -> str:
    """
    Get the test database URL.
    
    Uses SQLite by default for fast testing, can switch to PostgreSQL
    by setting TEST_DB=postgres environment variable.
    """
    test_db = os.environ.get("TEST_DB", "sqlite")
    
    if test_db.lower() == "postgres":
        # Use PostgreSQL for testing
        test_host = os.environ.get("TEST_PG_HOST", "localhost")
        test_port = os.environ.get("TEST_PG_PORT", "5432")
        test_user = os.environ.get("TEST_PG_USER", "postgres")
        test_password = os.environ.get("TEST_PG_PASSWORD", "postgres")
        test_db_name = os.environ.get("TEST_PG_DB", "test_twinsecure")
        
        encoded_password = quote_plus(test_password)
        return f"postgresql+asyncpg://{test_user}:{encoded_password}@{test_host}:{test_port}/{test_db_name}"
    
    # Use SQLite for testing (file-based for persistence across tests)
    return "sqlite+aiosqlite:///./test.db"
