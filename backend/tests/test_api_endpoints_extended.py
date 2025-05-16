import pytest
from fastapi.testclient import TestClient

# Import the mock app instead of the real app
from tests.mock_app import app

# Create a test client
client = TestClient(app)

def test_auth_login_logout_extended():
    response = client.post("/api/v1/auth/login", data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401

def test_alerts_crud_extended():
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 401

def test_users_crud_extended():
    response = client.get("/api/v1/users/")
    assert response.status_code == 401

def test_system_health_extended():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_reports_endpoint():
    response = client.get("/api/v1/reports/")
    assert response.status_code == 401

def test_honeypot_endpoint():
    response = client.get("/api/v1/honeypot/")
    assert response.status_code == 401
