"""
PostgreSQL database integration tests.
These tests verify that the application works correctly with a PostgreSQL database.
"""

import uuid
from typing import Any, AsyncGenerator, Dict

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AlertSeverity, AlertStatus, AlertType, UserRole
from app.db.models.alert import Alert
from app.db.models.user import User

# Import test fixtures
from tests.conftest import app, client, superuser_auth_headers, user_auth_headers

# Import PostgreSQL test utilities
from tests.pg_test_utils import (
    TEST_DATABASE_URL,
    create_test_alert,
    create_test_user,
    get_test_db,
    init_test_db,
)

# Skip all tests in this module since PostgreSQL is not available
pytestmark = pytest.mark.skip(reason="PostgreSQL is not available for testing")


@pytest.fixture(scope="module")
async def pg_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database for each test module.
    """
    # Initialize the database
    await init_test_db()

    # Get a database session
    async for session in get_test_db():
        yield session


@pytest.mark.asyncio
async def test_user_creation(pg_db: AsyncSession):
    """Test user creation in PostgreSQL."""
    # Create a test user
    email = f"test-{uuid.uuid4()}@example.com"
    user = await create_test_user(pg_db, email=email)

    # Verify the user was created
    assert user.id is not None
    assert user.email == email
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.role == UserRole.VIEWER


@pytest.mark.asyncio
async def test_superuser_creation(pg_db: AsyncSession):
    """Test superuser creation in PostgreSQL."""
    # Create a test superuser
    email = f"admin-{uuid.uuid4()}@example.com"
    user = await create_test_user(
        pg_db, email=email, is_superuser=True, role=UserRole.ADMIN
    )

    # Verify the superuser was created
    assert user.id is not None
    assert user.email == email
    assert user.is_active is True
    assert user.is_superuser is True
    assert user.role == UserRole.ADMIN


@pytest.mark.asyncio
async def test_alert_creation(pg_db: AsyncSession):
    """Test alert creation in PostgreSQL."""
    # Create a test alert
    title = f"Test Alert {uuid.uuid4()}"
    alert = await create_test_alert(pg_db, title=title)

    # Verify the alert was created
    assert alert.id is not None
    assert alert.title == title
    assert alert.severity == AlertSeverity.MEDIUM
    assert alert.status == AlertStatus.NEW
    assert alert.alert_type == AlertType.HONEYPOT_TRIGGER


@pytest.mark.asyncio
async def test_alert_update(pg_db: AsyncSession):
    """Test alert update in PostgreSQL."""
    # Create a test alert
    alert = await create_test_alert(pg_db)

    # Update the alert
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.severity = AlertSeverity.HIGH
    pg_db.add(alert)
    await pg_db.commit()
    await pg_db.refresh(alert)

    # Verify the alert was updated
    assert alert.status == AlertStatus.ACKNOWLEDGED
    assert alert.severity == AlertSeverity.HIGH


@pytest.mark.asyncio
async def test_alert_delete(pg_db: AsyncSession):
    """Test alert deletion in PostgreSQL."""
    # Create a test alert
    alert = await create_test_alert(pg_db)

    # Delete the alert
    await pg_db.delete(alert)
    await pg_db.commit()

    # Verify the alert was deleted
    deleted_alert = await pg_db.get(Alert, alert.id)
    assert deleted_alert is None


@pytest.mark.asyncio
async def test_user_authentication(pg_db: AsyncSession):
    """Test user authentication in PostgreSQL."""
    # Create a test user
    email = f"auth-{uuid.uuid4()}@example.com"
    password = "testpassword123"
    await create_test_user(pg_db, email=email, password=password)

    # Test authentication (this is a simplified test)
    # In a real test, you would use the login endpoint
    user = await pg_db.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.email == email


@pytest.mark.asyncio
async def test_user_roles(pg_db: AsyncSession):
    """Test user roles in PostgreSQL."""
    # Create users with different roles
    viewer = await create_test_user(
        pg_db, email=f"viewer-{uuid.uuid4()}@example.com", role=UserRole.VIEWER
    )
    analyst = await create_test_user(
        pg_db, email=f"analyst-{uuid.uuid4()}@example.com", role=UserRole.ANALYST
    )
    admin = await create_test_user(
        pg_db,
        email=f"admin-{uuid.uuid4()}@example.com",
        role=UserRole.ADMIN,
        is_superuser=True,
    )

    # Verify the roles
    assert viewer.role == UserRole.VIEWER
    assert analyst.role == UserRole.ANALYST
    assert admin.role == UserRole.ADMIN
    assert admin.is_superuser is True


@pytest.mark.asyncio
async def test_alert_assignment(pg_db: AsyncSession):
    """Test alert assignment in PostgreSQL."""
    # Create a test user
    user = await create_test_user(pg_db)

    # Create a test alert assigned to the user
    alert = await create_test_alert(pg_db, assigned_to_id=user.id)

    # Verify the alert was assigned
    assert alert.assigned_to_id == user.id
