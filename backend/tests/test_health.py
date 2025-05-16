import pytest
from fastapi.testclient import TestClient

# Import the mock app instead of the real app
from tests.mock_app import app

# Create a test client
client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data