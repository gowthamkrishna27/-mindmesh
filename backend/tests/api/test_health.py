"""API tests for the health check endpoints."""

from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.db.session import get_db
from app.main import app


def test_root_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["version"] == "3.0.0"
    assert "environment" in data


def test_api_v1_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["version"] == "3.0.0"


def test_health_endpoint_degraded_when_db_fails(client: TestClient):
    mock_db = MagicMock()
    mock_db.execute.side_effect = RuntimeError("Database connection lost")

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get("/health")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "degraded"
        assert "unhealthy" in data["database"]
    finally:
        app.dependency_overrides.clear()
