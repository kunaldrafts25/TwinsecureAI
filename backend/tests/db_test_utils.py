"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

"""
Database utilities for testing.
This module provides utilities for setting up and tearing down test databases.
"""

import asyncio
import os
import time

# Define missing enums if they don't exist in the app
from enum import Enum
from typing import Any, AsyncGenerator, Dict, Generator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.enums import AlertSeverity, AlertStatus, UserRole

# Import app modules
from app.db.base import Base
from app.db.models.alert import Alert
from app.db.models.user import User

try:
    from app.core.enums import AlertType
except ImportError:

    class AlertType(str, Enum):
        INTRUSION = "INTRUSION"
        MALWARE = "MALWARE"
        PHISHING = "PHISHING"
        VULNERABILITY = "VULNERABILITY"
        SUSPICIOUS = "SUSPICIOUS"
        POLICY_VIOLATION = "POLICY_VIOLATION"


try:
    from app.core.enums import AlertSource
except ImportError:

    class AlertSource(str, Enum):
        HONEYPOT = "HONEYPOT"
        IDS = "IDS"
        FIREWALL = "FIREWALL"
        SIEM = "SIEM"
        MANUAL = "MANUAL"


from app.core.password import get_password_hash

# Use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine with NullPool to avoid connection issues in tests
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
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


class AsyncSessionContext:
    """Context manager for async database sessions."""

    def __init__(self):
        self.session = TestingSessionLocal()

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()


def get_test_db():
    """
    Get a test database session as a context manager.
    """
    return AsyncSessionContext()


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
    severity: AlertSeverity = AlertSeverity.MEDIUM,
    status: AlertStatus = AlertStatus.NEW,
    source_ip: str = "192.168.1.100",
    assigned_to_id=None,
) -> Alert:
    """
    Create a test alert in the database.
    """
    # Create alert with required fields
    alert = Alert(
        title=title,
        severity=severity,
        status=status,
        source_ip=source_ip,
        description="Test alert description",
        assigned_to_id=assigned_to_id,
    )

    # Set alert_type and source if the fields exist
    try:
        # Import the enums here to avoid circular imports
        from app.core.enums import AlertType
        from app.db.models.alert import AlertSource

        # Set the alert_type field
        alert.alert_type = AlertType.HONEYPOT_TRIGGER

        # Set the source field
        alert.source = AlertSource.HONEYPOT
    except (AttributeError, TypeError, ImportError) as e:
        print(f"Warning: Could not set alert_type or source: {e}")
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


async def close_engine():
    """
    Close the test engine to release all connections.
    """
    try:
        await test_engine.dispose()
    except Exception as e:
        print(f"Error disposing engine: {e}")


def cleanup_test_db() -> None:
    """
    Clean up the test database by removing the SQLite file.
    """
    # Run the close_engine function in a new event loop
    try:
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Define a wrapper function that properly handles the coroutine
        async def close_and_cleanup():
            try:
                # Close the engine first
                await close_engine()
            except Exception as e:
                print(f"Error in close_engine: {e}")

        # Run the wrapper function
        try:
            loop.run_until_complete(close_and_cleanup())
        finally:
            loop.close()
            asyncio.set_event_loop(None)
    except Exception as e:
        print(f"Error in cleanup process: {e}")

    # Try to remove the file with retries
    max_retries = 5
    for i in range(max_retries):
        try:
            if os.path.exists("./test.db"):
                os.remove("./test.db")
            break
        except PermissionError:
            if i < max_retries - 1:
                print(
                    f"Could not remove database file, retrying ({i+1}/{max_retries})..."
                )
                time.sleep(0.5)  # Wait a bit before retrying
            else:
                print("Could not remove database file after multiple attempts.")
