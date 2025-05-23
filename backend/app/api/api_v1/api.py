"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

from fastapi import APIRouter

# Import endpoint routers
from app.api.api_v1.endpoints import (
    alerts,
    auth,
    dashboard,
    honeypot,
    reports,
    system,
    users,
)

# Create the main router for API version 1
api_router = APIRouter()

# Include endpoint routers with prefixes and tags
api_router.include_router(auth, prefix="/auth", tags=["Authentication"])
api_router.include_router(alerts, prefix="/alerts", tags=["Alerts"])
api_router.include_router(reports, prefix="/reports", tags=["Reports"])
api_router.include_router(honeypot, prefix="/honeypot", tags=["Honeypot"])
api_router.include_router(system, prefix="/system", tags=["System Status"])
api_router.include_router(dashboard, prefix="/dashboard", tags=["Dashboard"])

# Optional: Include user management endpoints if needed
api_router.include_router(users, prefix="/users", tags=["Users"])


# You could add a root endpoint for the v1 API here if desired
@api_router.get("/", status_code=200)
def read_api_root():
    return {"message": "Welcome to TwinSecure AI API v1"}


# Health check endpoint for the API
@api_router.get("/health", status_code=200)
def health_check():
    """
    Health check endpoint for the API.
    """
    return {"status": "ok", "message": "API is healthy"}
