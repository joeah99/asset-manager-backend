import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_ping_endpoint():
    """Test the ping endpoint returns correct status"""
    response = client.get("/api/commodities/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "commodity-tracker"

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Python backend is running!" in data["message"]

def test_ping_endpoint_response_structure():
    """Test ping endpoint response structure"""
    response = client.get("/api/commodities/ping")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert "service" in data

