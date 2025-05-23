"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

"""
Tests for honeypot endpoints.
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


def test_get_honeypot_authenticated(client, user_auth_headers):
    """Test getting honeypot data with authentication."""
    response = client.get("/api/v1/honeypot/", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "events" in data
    assert isinstance(data["events"], list)
    assert len(data["events"]) > 0
    # Check event structure
    event = data["events"][0]
    assert "id" in event
    assert "timestamp" in event
    assert "source_ip" in event
    assert "event_type" in event
    assert "details" in event


def test_get_honeypot_unauthenticated(client):
    """Test getting honeypot data without authentication."""
    response = client.get("/api/v1/honeypot/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
