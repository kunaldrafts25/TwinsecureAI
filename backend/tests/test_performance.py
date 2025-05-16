"""
Performance tests.
These tests measure the performance of API endpoints.
"""

import statistics
from typing import Dict, List

import pytest
from fastapi.testclient import TestClient

# Import fixtures
from tests.conftest import (
    client,
    performance_timer,
    superuser_auth_headers,
    user_auth_headers,
)

# Define performance thresholds
MAX_RESPONSE_TIME = 0.5  # seconds
MAX_AVERAGE_RESPONSE_TIME = 0.2  # seconds


def test_health_endpoint_performance(client: TestClient, performance_timer):
    """Test the performance of the health endpoint."""
    # Perform multiple requests to get a reliable average
    response_times = []
    for _ in range(10):
        timer = performance_timer.start()
        response = client.get("/health")
        timer.stop()
        assert response.status_code == 200
        response_times.append(timer.duration())

    # Calculate statistics
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)

    # Print performance statistics
    print(f"\nHealth endpoint performance:")
    print(f"  Average response time: {avg_time:.4f} seconds")
    print(f"  Maximum response time: {max_time:.4f} seconds")
    print(f"  Minimum response time: {min_time:.4f} seconds")

    # Assert that the performance meets the requirements
    assert (
        max_time < MAX_RESPONSE_TIME
    ), f"Maximum response time ({max_time:.4f}s) exceeds threshold ({MAX_RESPONSE_TIME}s)"
    assert (
        avg_time < MAX_AVERAGE_RESPONSE_TIME
    ), f"Average response time ({avg_time:.4f}s) exceeds threshold ({MAX_AVERAGE_RESPONSE_TIME}s)"


def test_login_endpoint_performance(client: TestClient, performance_timer):
    """Test the performance of the login endpoint."""
    # Prepare login data
    login_data = {"username": "test@example.com", "password": "password"}

    # Perform multiple requests to get a reliable average
    response_times = []
    for _ in range(5):
        timer = performance_timer.start()
        response = client.post("/api/v1/auth/login", data=login_data)
        timer.stop()
        assert response.status_code in [
            200,
            401,
        ]  # Either success or invalid credentials
        response_times.append(timer.duration())

    # Calculate statistics
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)

    # Print performance statistics
    print(f"\nLogin endpoint performance:")
    print(f"  Average response time: {avg_time:.4f} seconds")
    print(f"  Maximum response time: {max_time:.4f} seconds")
    print(f"  Minimum response time: {min_time:.4f} seconds")

    # Assert that the performance meets the requirements
    assert (
        max_time < MAX_RESPONSE_TIME
    ), f"Maximum response time ({max_time:.4f}s) exceeds threshold ({MAX_RESPONSE_TIME}s)"
    assert (
        avg_time < MAX_AVERAGE_RESPONSE_TIME
    ), f"Average response time ({avg_time:.4f}s) exceeds threshold ({MAX_AVERAGE_RESPONSE_TIME}s)"


def test_alerts_endpoint_performance(
    client: TestClient, user_auth_headers: Dict[str, str], performance_timer
):
    """Test the performance of the alerts endpoint."""
    # Perform multiple requests to get a reliable average
    response_times = []
    for _ in range(5):
        timer = performance_timer.start()
        response = client.get("/api/v1/alerts/", headers=user_auth_headers)
        timer.stop()
        assert response.status_code == 200
        response_times.append(timer.duration())

    # Calculate statistics
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)

    # Print performance statistics
    print(f"\nAlerts endpoint performance:")
    print(f"  Average response time: {avg_time:.4f} seconds")
    print(f"  Maximum response time: {max_time:.4f} seconds")
    print(f"  Minimum response time: {min_time:.4f} seconds")

    # Assert that the performance meets the requirements
    assert (
        max_time < MAX_RESPONSE_TIME
    ), f"Maximum response time ({max_time:.4f}s) exceeds threshold ({MAX_RESPONSE_TIME}s)"
    assert (
        avg_time < MAX_AVERAGE_RESPONSE_TIME
    ), f"Average response time ({avg_time:.4f}s) exceeds threshold ({MAX_AVERAGE_RESPONSE_TIME}s)"


def test_create_alert_performance(
    client: TestClient, user_auth_headers: Dict[str, str], performance_timer
):
    """Test the performance of creating an alert."""
    # Prepare alert data
    alert_data = {
        "alert_type": "INTRUSION",
        "source_ip": "192.168.1.100",
        "severity": "HIGH",
        "status": "NEW",
        "title": "Performance Test Alert",
        "description": "Testing alert creation performance",
    }

    # Perform multiple requests to get a reliable average
    response_times = []
    for _ in range(3):
        timer = performance_timer.start()
        response = client.post(
            "/api/v1/alerts/", json=alert_data, headers=user_auth_headers
        )
        timer.stop()
        assert response.status_code == 200
        response_times.append(timer.duration())

    # Calculate statistics
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)

    # Print performance statistics
    print(f"\nCreate alert endpoint performance:")
    print(f"  Average response time: {avg_time:.4f} seconds")
    print(f"  Maximum response time: {max_time:.4f} seconds")
    print(f"  Minimum response time: {min_time:.4f} seconds")

    # Assert that the performance meets the requirements
    assert (
        max_time < MAX_RESPONSE_TIME
    ), f"Maximum response time ({max_time:.4f}s) exceeds threshold ({MAX_RESPONSE_TIME}s)"
    assert (
        avg_time < MAX_AVERAGE_RESPONSE_TIME
    ), f"Average response time ({avg_time:.4f}s) exceeds threshold ({MAX_AVERAGE_RESPONSE_TIME}s)"
