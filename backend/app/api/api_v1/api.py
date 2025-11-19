"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.

Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    alerts,
    auth,
    dashboard,
    digital_twin,
    honeypot,
    reports,
    system,
    users,
)

api_router = APIRouter()

api_router.include_router(auth, prefix="/auth", tags=["Authentication"])
api_router.include_router(users, prefix="/users", tags=["Users"])
api_router.include_router(alerts, prefix="/alerts", tags=["Alerts"])
api_router.include_router(reports, prefix="/reports", tags=["Reports"])
api_router.include_router(honeypot, prefix="/honeypot", tags=["Honeypot"])
api_router.include_router(digital_twin, prefix="/digital-twins", tags=["Digital Twins"])
api_router.include_router(system, prefix="/system", tags=["System Status"])
api_router.include_router(dashboard, prefix="/dashboard", tags=["Dashboard"])


@api_router.get("/", status_code=200)
def read_api_root() -> dict[str, str]:
    """API v1 root endpoint."""
    return {"message": "Welcome to TwinSecure AI API v1"}


@api_router.get("/health", status_code=200)
def health_check() -> dict[str, str]:
    """Health check endpoint for the API."""
    return {"status": "ok", "message": "API is healthy"}
