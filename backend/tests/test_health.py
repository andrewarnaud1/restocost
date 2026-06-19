"""Tests for health check endpoints."""

from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient


def test_health_check_success(client: TestClient) -> None:
    """Test successful health check.

    Args:
        client: FastAPI test client.
    """
    # Act
    response = client.get("/api/health")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_health_check_db_success(client: TestClient) -> None:
    """Test successful database health check.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch(
        "app.routers.health.check_db_connection", return_value=True
    ) as mock_check:
        # Act
        response = client.get("/api/health/db")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}
        mock_check.assert_called_once()


def test_health_check_db_failure(client: TestClient) -> None:
    """Test database health check when database is unavailable.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch(
        "app.routers.health.check_db_connection", return_value=False
    ) as mock_check:
        # Act
        response = client.get("/api/health/db")

        # Assert
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json() == {"detail": "Database connection failed"}
        mock_check.assert_called_once()


def test_health_check_response_format(client: TestClient) -> None:
    """Test health check returns correct response format.

    Args:
        client: FastAPI test client.
    """
    # Act
    response = client.get("/api/health")
    data = response.json()

    # Assert
    assert isinstance(data, dict)
    assert "status" in data
    assert data["status"] == "ok"


def test_health_check_db_response_format_success(client: TestClient) -> None:
    """Test database health check returns correct response format on success.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch("app.routers.health.check_db_connection", return_value=True):
        # Act
        response = client.get("/api/health/db")
        data = response.json()

        # Assert
        assert isinstance(data, dict)
        assert "status" in data
        assert data["status"] == "ok"


def test_health_check_db_response_format_failure(client: TestClient) -> None:
    """Test database health check returns correct error format on failure.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch("app.routers.health.check_db_connection", return_value=False):
        # Act
        response = client.get("/api/health/db")
        data = response.json()

        # Assert
        assert isinstance(data, dict)
        assert "detail" in data
        assert data["detail"] == "Database connection failed"
