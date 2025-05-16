"""
Authentication API endpoint tests.

This module contains tests for the authentication endpoints, including:
- Login
- Token refresh
- Password reset
- User registration
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.db.models.user import User
from app.schemas.token import Token

# Import test utilities
from .conftest import override_get_db, create_test_user

# Override the database dependency
app.dependency_overrides[override_get_db] = override_get_db

# Create a test client
client = TestClient(app)

@pytest.mark.asyncio
async def test_login_success(db_session: AsyncSession):
    """Test successful login with valid credentials."""
    # Create a test user
    email = "test_login@example.com"
    password = "testpassword123"
    hashed_password = get_password_hash(password)
    
    # Create user in the database
    user = await create_test_user(db_session, email=email, hashed_password=hashed_password)
    
    # Attempt login
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password}
    )
    
    # Check response
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "token_type" == "bearer"
    
    # Verify token contains correct user info
    payload = jwt.decode(
        token_data["access_token"], 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == str(user.id)
    assert payload["email"] == email

@pytest.mark.asyncio
async def test_login_invalid_password(db_session: AsyncSession):
    """Test login with invalid password."""
    # Create a test user
    email = "test_invalid_pw@example.com"
    password = "testpassword123"
    hashed_password = get_password_hash(password)
    
    # Create user in the database
    await create_test_user(db_session, email=email, hashed_password=hashed_password)
    
    # Attempt login with wrong password
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": "wrongpassword"}
    )
    
    # Check response
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "Incorrect" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_nonexistent_user():
    """Test login with non-existent user."""
    # Attempt login with non-existent user
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "nonexistent@example.com", "password": "testpassword123"}
    )
    
    # Check response
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "Incorrect" in response.json()["detail"]

@pytest.mark.asyncio
async def test_refresh_token_success(db_session: AsyncSession):
    """Test successful token refresh."""
    # Create a test user
    email = "test_refresh@example.com"
    user = await create_test_user(db_session, email=email)
    
    # Create a valid refresh token
    refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        data={"sub": str(user.id), "email": email, "token_type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    # Attempt to refresh token
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    # Check response
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    # Verify token contains correct user info
    payload = jwt.decode(
        token_data["access_token"], 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == str(user.id)
    assert payload["email"] == email

@pytest.mark.asyncio
async def test_refresh_token_invalid():
    """Test token refresh with invalid token."""
    # Attempt to refresh with invalid token
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )
    
    # Check response
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "Invalid" in response.json()["detail"]

@pytest.mark.asyncio
async def test_refresh_token_expired(db_session: AsyncSession):
    """Test token refresh with expired token."""
    # Create a test user
    email = "test_expired@example.com"
    user = await create_test_user(db_session, email=email)
    
    # Create an expired refresh token
    refresh_token_expires = datetime.utcnow() - timedelta(days=1)
    refresh_token = create_access_token(
        data={"sub": str(user.id), "email": email, "token_type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    # Attempt to refresh token
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    # Check response
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "expired" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_register_user_success():
    """Test successful user registration."""
    # User data for registration
    user_data = {
        "email": "new_user@example.com",
        "password": "StrongPassword123!",
        "full_name": "New User"
    }
    
    # Attempt to register
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=user_data
    )
    
    # Check response
    assert response.status_code == 201
    user_response = response.json()
    assert user_response["email"] == user_data["email"]
    assert user_response["full_name"] == user_data["full_name"]
    assert "id" in user_response
    assert "password" not in user_response

@pytest.mark.asyncio
async def test_register_user_existing_email(db_session: AsyncSession):
    """Test user registration with existing email."""
    # Create a test user
    email = "existing@example.com"
    await create_test_user(db_session, email=email)
    
    # User data for registration with existing email
    user_data = {
        "email": email,
        "password": "StrongPassword123!",
        "full_name": "Existing User"
    }
    
    # Attempt to register
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=user_data
    )
    
    # Check response
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "already exists" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_register_user_weak_password():
    """Test user registration with weak password."""
    # User data for registration with weak password
    user_data = {
        "email": "weak_password@example.com",
        "password": "weak",
        "full_name": "Weak Password User"
    }
    
    # Attempt to register
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=user_data
    )
    
    # Check response
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "password" in str(response.json()["detail"]).lower()
