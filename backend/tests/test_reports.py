"""
Tests for report endpoints.
"""
import pytest
from fastapi.testclient import TestClient

# Import fixtures
from tests.conftest import client, user_token, superuser_token, user_auth_headers, superuser_auth_headers

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
