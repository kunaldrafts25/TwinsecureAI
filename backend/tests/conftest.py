"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

"""
Configuration file for pytest.
This file sets up the Python path to allow importing from the app module
and provides fixtures for testing.

Fixtures provided:
- client: FastAPI TestClient for testing endpoints
- user_token, superuser_token: Mock JWT tokens
- user_auth_headers, superuser_auth_headers: Authentication headers
- db: Database session for testing
- test_db_user, test_db_superuser: Test users in the database
- test_db_alerts: Test alerts in the database
- db_user_token, db_superuser_token: Real JWT tokens for database users
- db_user_auth_headers, db_superuser_auth_headers: Authentication headers for database users
- performance_timer: Timer for performance testing
- db_session: Async database session for direct database access
- override_get_db: Function to override the database dependency in FastAPI
"""

import asyncio
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Generator, List
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to allow importing from app
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Check if PostgreSQL is available
try:
    # Run the check_postgres script to set environment variables
    from tests.check_postgres import main as check_postgres

    # Use a separate event loop for initialization to avoid issues with pytest-asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(check_postgres())
    finally:
        loop.close()
        asyncio.set_event_loop(None)
except Exception as e:
    print(f"PostgreSQL check failed: {e}")
    os.environ["USE_POSTGRES_FOR_TESTS"] = "false"

# Determine which database utilities to use
USE_POSTGRES = os.getenv("USE_POSTGRES_FOR_TESTS", "false").lower() == "true"

# Import app modules after setting up sys.path
from tests.mock_app import app

if USE_POSTGRES:
    print("Using PostgreSQL for tests")
    from tests.pg_test_utils import (
        TEST_DATABASE_URL,
        cleanup_test_db,
        create_test_alert,
        create_test_user,
        get_test_db,
        init_test_db,
    )
else:
    print("Using SQLite for tests")
    from tests.db_test_utils import (
        TEST_DATABASE_URL,
        cleanup_test_db,
        create_test_alert,
        create_test_user,
        get_test_db,
        init_test_db,
    )

try:
    from app.core.enums import AlertSeverity, AlertStatus, UserRole
    from app.core.security import create_access_token
    from app.db.base import Base

    DB_IMPORTS_AVAILABLE = True
except ImportError:
    DB_IMPORTS_AVAILABLE = False


# Test client fixture
@pytest.fixture(scope="function")
def client() -> Generator:
    """
    Create a FastAPI TestClient for testing endpoints.
    """
    with TestClient(app) as test_client:
        yield test_client


# Token fixtures
@pytest.fixture(scope="function")
def user_token() -> str:
    """
    Create a mock JWT token for a regular user.
    """
    # Create a mock token with a fixed user ID
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    return f"mock_token_{user_id}"


@pytest.fixture(scope="function")
def superuser_token() -> str:
    """
    Create a mock JWT token for a superuser.
    """
    # Create a mock token with a fixed superuser ID
    superuser_id = "550e8400-e29b-41d4-a716-446655440001"
    return f"mock_token_{superuser_id}"


# Authentication header fixtures
@pytest.fixture(scope="function")
def user_auth_headers(user_token: str) -> dict:
    """
    Create authentication headers for a regular user.
    """
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(scope="function")
def superuser_auth_headers(superuser_token: str) -> dict:
    """
    Create authentication headers for a superuser.
    """
    return {"Authorization": f"Bearer {superuser_token}"}


# Database fixtures - only used when testing with a real database
if DB_IMPORTS_AVAILABLE:

    @pytest.fixture(scope="function")
    async def db():
        """
        Create a fresh database for each test.
        """
        await init_test_db()

        # Use a try-finally block to ensure cleanup happens
        try:
            async with get_test_db() as session:
                yield session
        finally:
            # Always clean up the database after the test
            cleanup_test_db()

    @pytest.fixture(scope="function")
    async def test_db_user(db: AsyncSession) -> Dict[str, Any]:
        """
        Create a test user in the database.
        """
        user = await create_test_user(
            db=db,
            email="dbtest@example.com",
            password="testpassword",
            is_superuser=False,
            role=UserRole.VIEWER,
        )
        return {
            "id": str(user.id),
            "email": user.email,
            "is_superuser": user.is_superuser,
            "role": user.role.value,
        }

    @pytest.fixture(scope="function")
    async def test_db_superuser(db: AsyncSession) -> Dict[str, Any]:
        """
        Create a test superuser in the database.
        """
        user = await create_test_user(
            db=db,
            email="dbadmin@example.com",
            password="adminpassword",
            is_superuser=True,
            role=UserRole.ADMIN,
        )
        return {
            "id": str(user.id),
            "email": user.email,
            "is_superuser": user.is_superuser,
            "role": user.role.value,
        }

    @pytest.fixture(scope="function")
    async def test_db_alerts(
        db: AsyncSession, test_db_user: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create test alerts in the database.
        """
        alerts = []
        # Create 5 test alerts
        for i in range(5):
            alert = await create_test_alert(
                db=db,
                title=f"Test Alert {i}",
                severity=AlertSeverity.MEDIUM if i % 2 == 0 else AlertSeverity.HIGH,
                status=AlertStatus.NEW if i % 3 == 0 else AlertStatus.ACKNOWLEDGED,
                assigned_to_id=UUID(test_db_user["id"]) if i % 2 == 0 else None,
            )
            alerts.append(
                {
                    "id": str(alert.id),
                    "title": alert.title,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                }
            )
        return alerts

    @pytest.fixture(scope="function")
    def db_user_token(test_db_user: Dict[str, Any]) -> str:
        """
        Create a real JWT token for a database user.
        """
        return create_access_token(subject=test_db_user["id"])

    @pytest.fixture(scope="function")
    def db_superuser_token(test_db_superuser: Dict[str, Any]) -> str:
        """
        Create a real JWT token for a database superuser.
        """
        return create_access_token(subject=test_db_superuser["id"])

    @pytest.fixture(scope="function")
    def db_user_auth_headers(db_user_token: str) -> Dict[str, str]:
        """
        Create authentication headers for a database user.
        """
        return {"Authorization": f"Bearer {db_user_token}"}

    @pytest.fixture(scope="function")
    def db_superuser_auth_headers(db_superuser_token: str) -> Dict[str, str]:
        """
        Create authentication headers for a database superuser.
        """
        return {"Authorization": f"Bearer {db_superuser_token}"}


# Database session fixture for direct database access
@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.

    This fixture provides direct access to the database session,
    which is useful for tests that need to interact with the database
    directly rather than through the API.

    Returns:
        AsyncSession: SQLAlchemy async session
    """
    # Initialize test database
    await init_test_db()

    # Create a new session for the test
    async with get_test_db() as session:
        yield session

    # Clean up after the test
    await cleanup_test_db()


# Function to override the database dependency in FastAPI
async def override_get_db():
    """
    Override the database dependency in FastAPI.

    This function is used to replace the database dependency in FastAPI
    with a test database session for testing.

    Yields:
        AsyncSession: SQLAlchemy async session
    """
    async with get_test_db() as session:
        yield session


# Performance testing fixtures
@pytest.fixture(scope="function")
def performance_timer():
    """
    Timer fixture for performance testing.

    This fixture provides a simple timer for measuring the performance
    of code blocks during testing.

    Returns:
        Timer: Timer object with start, stop, and duration methods
    """

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()
            return self

        def stop(self):
            self.end_time = time.time()
            return self

        def duration(self):
            if self.start_time is None:
                raise ValueError("Timer not started")
            if self.end_time is None:
                self.stop()
            return self.end_time - self.start_time

    return Timer()
