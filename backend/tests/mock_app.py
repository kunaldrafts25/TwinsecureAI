"""
Mock app for testing purposes.
This file creates a simplified version of the main app for testing.
"""
from fastapi import FastAPI, Depends, HTTPException, Request, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

# Create a simple FastAPI app for testing
app = FastAPI(
    title="TwinSecure AI Backend Test",
    description="Test version of TwinSecure AI Backend",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Mock database for testing
class MockDB:
    users = {
        "test@example.com": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "test@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False,
            "role": "VIEWER"
        },
        "admin@example.com": {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "email": "admin@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            "full_name": "Admin User",
            "is_active": True,
            "is_superuser": True,
            "role": "ADMIN"
        }
    }

    alerts = [
        {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "alert_type": "INTRUSION",
            "source_ip": "192.168.1.100",
            "severity": "HIGH",
            "status": "NEW",
            "created_at": datetime.now().isoformat(),
            "title": "Suspicious Login Attempt",
            "description": "Multiple failed login attempts detected"
        },
        {
            "id": "650e8400-e29b-41d4-a716-446655440001",
            "alert_type": "MALWARE",
            "source_ip": "192.168.1.101",
            "severity": "MEDIUM",
            "status": "ACKNOWLEDGED",
            "created_at": datetime.now().isoformat(),
            "title": "Potential Malware Detected",
            "description": "Suspicious file activity detected"
        }
    ]

    reports = [
        {
            "id": "750e8400-e29b-41d4-a716-446655440000",
            "title": "Monthly Security Report",
            "description": "Security overview for the month",
            "created_at": datetime.now().isoformat(),
            "status": "COMPLETED"
        }
    ]

# Mock authentication dependency
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Mock dependency to get the current user from the Authorization header.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check if the token starts with "Bearer "
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Extract the token
    token = authorization.replace("Bearer ", "")

    # Check if it's a mock token for testing
    if token.startswith("mock_token_"):
        user_id = token.replace("mock_token_", "")
        # Return the user based on the ID
        for user in MockDB.users.values():
            if user["id"] == user_id:
                return user

    # If no user found, raise an exception
    raise HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

# Mock superuser dependency
async def get_current_superuser(current_user: dict = Depends(get_current_user)):
    """
    Mock dependency to check if the current user is a superuser.
    """
    if not current_user["is_superuser"]:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )
    return current_user

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint for testing.
    """
    return {"status": "ok"}

@app.get("/api/v1/system/health", tags=["Health"])
async def system_health():
    """
    System health check endpoint for testing.
    """
    return {
        "status": "ok",
        "components": {
            "database": "ok",
            "cache": "ok",
            "storage": "ok"
        }
    }

# Authentication endpoints
@app.post("/api/v1/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Mock login endpoint that returns a token for valid credentials.
    """
    # Check if the user exists
    user = MockDB.users.get(form_data.username)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"}
        )

    # Check if the password is correct (in a real app, you would verify the hash)
    if form_data.password != "password":  # For testing, we accept "password" for all users
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"}
        )

    # Return a token
    return {
        "access_token": f"mock_token_{user['id']}",
        "token_type": "bearer"
    }

# User endpoints
@app.get("/api/v1/users/me", tags=["Users"])
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user

@app.get("/api/v1/users/", tags=["Users"])
async def get_users(current_user: dict = Depends(get_current_superuser)):
    """
    Get all users (superuser only).
    """
    return list(MockDB.users.values())

# Alert endpoints
@app.get("/api/v1/alerts/", tags=["Alerts"])
async def get_alerts(current_user: dict = Depends(get_current_user)):
    """
    Get all alerts.
    """
    return MockDB.alerts

@app.get("/api/v1/alerts/{alert_id}", tags=["Alerts"])
async def get_alert(alert_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get a specific alert by ID.
    """
    for alert in MockDB.alerts:
        if alert["id"] == alert_id:
            return alert

    raise HTTPException(status_code=404, detail="Alert not found")

@app.post("/api/v1/alerts/", tags=["Alerts"])
async def create_alert(alert: dict, current_user: dict = Depends(get_current_user)):
    """
    Create a new alert.
    """
    new_alert = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        **alert
    }
    MockDB.alerts.append(new_alert)
    return new_alert

# Report endpoints
@app.get("/api/v1/reports/", tags=["Reports"])
async def get_reports(current_user: dict = Depends(get_current_user)):
    """
    Get all reports.
    """
    return MockDB.reports

# Honeypot endpoints
@app.get("/api/v1/honeypot/", tags=["Honeypot"])
async def get_honeypot(current_user: dict = Depends(get_current_user)):
    """
    Get honeypot data.
    """
    return {
        "status": "active",
        "events": [
            {
                "id": str(uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source_ip": "203.0.113.1",
                "event_type": "SSH_BRUTE_FORCE",
                "details": {
                    "attempts": 23,
                    "usernames": ["root", "admin", "user"]
                }
            }
        ]
    }
