"""
Tests for alert endpoints.
"""
import pytest
from fastapi.testclient import TestClient

# Import fixtures
from tests.conftest import client, user_token, superuser_token, user_auth_headers, superuser_auth_headers

def test_get_alerts_authenticated(client, user_auth_headers):
    """Test getting alerts with authentication."""
    response = client.get("/api/v1/alerts/", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check alert structure
    alert = data[0]
    assert "id" in alert
    assert "alert_type" in alert
    assert "severity" in alert
    assert "status" in alert
    assert "created_at" in alert

def test_get_alerts_unauthenticated(client):
    """Test getting alerts without authentication."""
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_get_specific_alert(client, user_auth_headers):
    """Test getting a specific alert by ID."""
    # First get all alerts
    response = client.get("/api/v1/alerts/", headers=user_auth_headers)
    alerts = response.json()
    alert_id = alerts[0]["id"]
    
    # Then get a specific alert
    response = client.get(f"/api/v1/alerts/{alert_id}", headers=user_auth_headers)
    assert response.status_code == 200
    alert = response.json()
    assert alert["id"] == alert_id

def test_get_nonexistent_alert(client, user_auth_headers):
    """Test getting a non-existent alert."""
    response = client.get(
        "/api/v1/alerts/999999999-9999-9999-9999-999999999999",
        headers=user_auth_headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Alert not found"}

def test_create_alert(client, user_auth_headers):
    """Test creating a new alert."""
    new_alert = {
        "alert_type": "PHISHING",
        "source_ip": "192.168.1.102",
        "severity": "HIGH",
        "status": "NEW",
        "title": "Phishing Email Detected",
        "description": "Suspicious email with malicious attachment"
    }
    
    response = client.post(
        "/api/v1/alerts/",
        json=new_alert,
        headers=user_auth_headers
    )
    assert response.status_code == 200
    created_alert = response.json()
    assert "id" in created_alert
    assert created_alert["alert_type"] == new_alert["alert_type"]
    assert created_alert["severity"] == new_alert["severity"]
    assert created_alert["title"] == new_alert["title"]
    assert "created_at" in created_alert
    
    # Verify the alert was added to the database
    response = client.get("/api/v1/alerts/", headers=user_auth_headers)
    alerts = response.json()
    assert any(alert["id"] == created_alert["id"] for alert in alerts)
