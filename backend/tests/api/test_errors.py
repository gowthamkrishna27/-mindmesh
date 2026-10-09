"""API tests for uniform error responses according to Specification v3 Section 11.13."""

from fastapi import status
from fastapi.testclient import TestClient


def test_404_not_found_error_format(client: TestClient):
    response = client.get("/api/v1/nonexistent-endpoint")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "message" in data["error"]
    assert "details" in data["error"]


def test_custom_app_errors(client: TestClient):
    from app.core.errors import BadRequestError, ConflictError, ForbiddenError, UnauthorizedError
    from app.main import app

    @app.get("/test-bad-request")
    def bad_request_route():
        raise BadRequestError("Invalid input parameters", details={"field": "test"})

    @app.get("/test-unauthorized")
    def unauthorized_route():
        raise UnauthorizedError("Missing token")

    @app.get("/test-forbidden")
    def forbidden_route():
        raise ForbiddenError("Access denied")

    @app.get("/test-conflict")
    def conflict_route():
        raise ConflictError("Resource duplicate")

    res = client.get("/test-bad-request")
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "BAD_REQUEST"
    assert res.json()["error"]["details"] == {"field": "test"}

    res = client.get("/test-unauthorized")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "UNAUTHORIZED"

    res = client.get("/test-forbidden")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"

    res = client.get("/test-conflict")
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "CONFLICT"

