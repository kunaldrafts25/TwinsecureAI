"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

"""
PostgreSQL database utilities for testing.
This module provides utilities for setting up and tearing down PostgreSQL test databases.
"""

import asyncio
import os
from typing import Any, AsyncGenerator, Dict, Generator, List
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.enums import AlertSeverity, AlertStatus, AlertType, UserRole
from app.core.password import get_password_hash

# Import app modules
from app.db.base import Base
from app.db.models.alert import Alert
from app.db.models.user import User

# Test database URL - use PostgreSQL for testing
# This can be overridden by environment variables
TEST_PG_HOST = os.getenv("TEST_PG_HOST", "localhost")
TEST_PG_PORT = os.getenv("TEST_PG_PORT", "5432")
TEST_PG_USER = os.getenv("TEST_PG_USER", "postgres")
TEST_PG_PASSWORD = os.getenv("TEST_PG_PASSWORD", "postgres")
TEST_PG_DB = os.getenv("TEST_PG_DB", "test_twinsecure")

# Construct the PostgreSQL connection URL
TEST_DATABASE_URL = f"postgresql+asyncpg://{TEST_PG_USER}:{TEST_PG_PASSWORD}@{TEST_PG_HOST}:{TEST_PG_PORT}/{TEST_PG_DB}"

# Create test engine with NullPool to avoid connection issues in tests
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_test_db() -> None:
    """
    Initialize the test database by creating all tables.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a test database session.
    """
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_test_user(
    db: AsyncSession,
    email: str = "test@example.com",
    password: str = "password",
    is_superuser: bool = False,
    role: UserRole = UserRole.VIEWER,
) -> User:
    """
    Create a test user in the database.
    """
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=f"Test User {email}",
        is_active=True,
        is_superuser=is_superuser,
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_test_alert(
    db: AsyncSession,
    title: str = "Test Alert",
    alert_type: AlertType = AlertType.HONEYPOT_TRIGGER,
    severity: AlertSeverity = AlertSeverity.MEDIUM,
    status: AlertStatus = AlertStatus.NEW,
    source_ip: str = "192.168.1.100",
    assigned_to_id=None,
) -> Alert:
    """
    Create a test alert in the database.
    """
    alert = Alert(
        title=title,
        alert_type=alert_type,
        severity=severity,
        status=status,
        source_ip=source_ip,
        description="Test alert description",
        assigned_to_id=assigned_to_id,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


def get_test_settings() -> Dict[str, Any]:
    """
    Get test settings for the application.
    """
    return {
        "ENVIRONMENT": "test",
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "API_V1_STR": "/api/v1",
        "PROJECT_NAME": "TwinSecure Test",
        "SECURITY__SECRET_KEY": "test_secret_key",
        "SECURITY__ALGORITHM": "HS256",
        "SECURITY__ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        "DATABASE_URL": TEST_DATABASE_URL,
    }


def cleanup_test_db() -> None:
    """
    Clean up the test database.
    """
    pass  # PostgreSQL handles cleanup automatically
