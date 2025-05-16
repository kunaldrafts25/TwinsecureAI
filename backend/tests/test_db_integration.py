"""
Database integration tests.
These tests use a real SQLite database to test database operations.
"""

import asyncio
from typing import Any, Dict, List
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import from conftest to check if database imports are available
from tests.conftest import DB_IMPORTS_AVAILABLE

# Run all tests since database imports are available
# pytestmark = pytest.mark.skipif(
#     not DB_IMPORTS_AVAILABLE,
#     reason="Database imports not available"
# )


# Test user creation and retrieval
@pytest.mark.asyncio
async def test_user_creation(db: AsyncSession, test_db_user: Dict[str, Any]):
    """Test that a user can be created in the database."""
    from app.db import crud

    # Get the user from the database
    user = await crud.user.get_by_email(db, email=test_db_user["email"])

    # Check that the user exists and has the correct attributes
    assert user is not None
    assert user.email == test_db_user["email"]
    assert user.is_superuser == test_db_user["is_superuser"]
    assert user.role.value == test_db_user["role"]


@pytest.mark.asyncio
async def test_superuser_creation(db: AsyncSession, test_db_superuser: Dict[str, Any]):
    """Test that a superuser can be created in the database."""
    from app.db import crud

    # Get the user from the database
    user = await crud.user.get_by_email(db, email=test_db_superuser["email"])

    # Check that the user exists and has the correct attributes
    assert user is not None
    assert user.email == test_db_superuser["email"]
    assert user.is_superuser == test_db_superuser["is_superuser"]
    assert user.role.value == test_db_superuser["role"]


# Test alert creation and retrieval
@pytest.mark.asyncio
async def test_alert_creation(db: AsyncSession, test_db_alerts: List[Dict[str, Any]]):
    """Test that alerts can be created in the database."""
    from app.db.crud.crud_alert import alert
    from app.schemas.alert import AlertQueryFilters

    # Create a default filter
    filters = AlertQueryFilters(limit=100, offset=0)

    # Check that we have the expected number of alerts
    alerts = await alert.get_multi(db, filters=filters)
    assert len(alerts) == len(test_db_alerts)

    # Check that each alert has the correct attributes
    for i, alert_data in enumerate(test_db_alerts):
        alert_obj = await alert.get(db, alert_id=UUID(alert_data["id"]))
        assert alert_obj is not None
        assert alert_obj.title == alert_data["title"]
        assert alert_obj.severity.value == alert_data["severity"]
        assert alert_obj.status.value == alert_data["status"]


@pytest.mark.asyncio
async def test_alert_update(db: AsyncSession, test_db_alerts: List[Dict[str, Any]]):
    """Test that alerts can be updated in the database."""
    from app.core.enums import AlertStatus
    from app.db.crud.crud_alert import alert

    # Get the first alert
    alert_id = UUID(test_db_alerts[0]["id"])
    alert_obj = await alert.get(db, alert_id=alert_id)

    # Update the alert
    updated_alert = await alert.update(
        db,
        db_obj=alert_obj,
        obj_in={"status": AlertStatus.RESOLVED, "title": "Updated Alert Title"},
    )

    # Check that the alert was updated
    assert updated_alert.status == AlertStatus.RESOLVED
    assert updated_alert.title == "Updated Alert Title"

    # Verify the update in the database
    alert_obj = await alert.get(db, alert_id=alert_id)
    assert alert_obj.status == AlertStatus.RESOLVED
    assert alert_obj.title == "Updated Alert Title"


@pytest.mark.asyncio
async def test_alert_delete(db: AsyncSession, test_db_alerts: List[Dict[str, Any]]):
    """Test that alerts can be deleted from the database."""
    from app.db.crud.crud_alert import alert
    from app.schemas.alert import AlertQueryFilters

    # Create a default filter
    filters = AlertQueryFilters(limit=100, offset=0)

    # Get the initial count of alerts
    initial_count = len(await alert.get_multi(db, filters=filters))

    # Delete the first alert
    alert_id = UUID(test_db_alerts[0]["id"])
    await alert.delete(db, alert_id=alert_id)

    # Check that the alert was deleted
    alerts = await alert.get_multi(db, filters=filters)
    assert len(alerts) == initial_count - 1

    # Check that the alert no longer exists
    alert_obj = await alert.get(db, alert_id=alert_id)
    assert alert_obj is None


# Test user authentication
@pytest.mark.asyncio
async def test_user_authentication(db: AsyncSession, test_db_user: Dict[str, Any]):
    """Test that a user can be authenticated."""
    from app.db import crud

    # Authenticate with correct credentials
    user = await crud.user.authenticate(
        db, email=test_db_user["email"], password="testpassword"
    )
    assert user is not None
    assert user.email == test_db_user["email"]

    # Authenticate with incorrect password
    user = await crud.user.authenticate(
        db, email=test_db_user["email"], password="wrongpassword"
    )
    assert user is None

    # Authenticate with non-existent user
    user = await crud.user.authenticate(
        db, email="nonexistent@example.com", password="testpassword"
    )
    assert user is None
