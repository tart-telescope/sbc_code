"""
Basic tests for the FastAPI TART telescope API.

These tests verify that the application starts correctly and basic endpoints work.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint returns expected response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "TART Telescope API"
    assert data["status"] == "running"


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_openapi_docs(client):
    """Test that OpenAPI documentation is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert data["info"]["title"] == "TART Telescope API"


def test_swagger_ui(client):
    """Test that Swagger UI is available."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()


def test_redoc(client):
    """Test that ReDoc is available."""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "redoc" in response.text.lower()


def test_info_endpoint_without_config(client):
    """Test info endpoint with basic configuration."""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert "name" in data["info"]
    assert "location" in data["info"]


def test_mode_endpoint(client):
    """Test mode endpoint returns available modes."""
    response = client.get("/mode")
    assert response.status_code == 200
    data = response.json()
    assert "modes" in data
    assert isinstance(data["modes"], list)
    assert len(data["modes"]) > 0


def test_current_mode_endpoint(client):
    """Test current mode endpoint."""
    response = client.get("/mode/current")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data
    assert data["mode"] in [
        "off",
        "diag",
        "raw",
        "vis",
        "vis_save",
        "cal",
        "rt_syn_img",
    ]


def test_status_fpga_endpoint(client):
    """Test FPGA status endpoint."""
    response = client.get("/status/fpga")
    assert response.status_code == 200
    # Response may be empty dict if no status available
    assert isinstance(response.json(), dict)


def test_status_channel_endpoint(client):
    """Test channel status endpoint."""
    response = client.get("/status/channel")
    assert response.status_code == 200
    # Response may be empty list if no channels configured
    assert isinstance(response.json(), list)


def test_auth_endpoint_bad_credentials(client):
    """Test authentication with bad credentials."""
    response = client.post("/auth/", json={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401
    data = response.json()
    assert "Bad username or password" in data["detail"]


def test_auth_endpoint_good_credentials(client):
    """Test authentication with correct credentials."""
    response = client.post("/auth/", json={"username": "admin", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)


def test_protected_endpoint_without_auth(client):
    """Test that protected endpoints require authentication."""
    response = client.post("/mode/off")
    assert response.status_code == 401


def test_protected_endpoint_with_auth(client):
    """Test that protected endpoints work with authentication."""
    # First, get a token
    auth_response = client.post(
        "/auth/", json={"username": "admin", "password": "password"}
    )
    token = auth_response.json()["access_token"]

    # Then use the token to access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/mode/off", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "off"
