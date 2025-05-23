"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

"""
Tests for report endpoints.
"""

import pytest
from fastapi.testclient import TestClient

# Import fixtures
from tests.conftest import (
    client,
    superuser_auth_headers,
    superuser_token,
    user_auth_headers,
    user_token,
)


def test_get_reports_authenticated(client, user_auth_headers):
    """Test getting reports with authentication."""
    response = client.get("/api/v1/reports/", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check report structure
    report = data[0]
    assert "id" in report
    assert "title" in report
    assert "description" in report
    assert "created_at" in report
    assert "status" in report


def test_get_reports_unauthenticated(client):
    """Test getting reports without authentication."""
    response = client.get("/api/v1/reports/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
