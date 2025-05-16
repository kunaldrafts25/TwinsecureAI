"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient

# Import fixtures
from tests.conftest import client, user_token, superuser_token, user_auth_headers, superuser_auth_headers

def test_login_success(client):
    """Test successful login with valid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent@example.com", "password": "password"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

def test_get_current_user(client, user_auth_headers):
    """Test getting current user information."""
    response = client.get("/api/v1/users/me", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_superuser"] is False

def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}

def test_superuser_access(client, superuser_auth_headers):
    """Test superuser access to protected endpoint."""
    response = client.get("/api/v1/users/", headers=superuser_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_regular_user_access_forbidden(client, user_auth_headers):
    """Test regular user access to superuser-only endpoint."""
    response = client.get("/api/v1/users/", headers=user_auth_headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}
