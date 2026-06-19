"""Tests for authentication endpoints."""

from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from app.models.user import User


def test_register_success(client: TestClient) -> None:
    """Test successful user registration.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch("app.routers.auth.get_user_by_email", return_value=None), patch(
        "app.routers.auth.create_user"
    ) as mock_create, patch("app.routers.auth.create_user_tokens") as mock_tokens:
        # Setup mocks
        mock_user = AsyncMock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_create.return_value = mock_user

        mock_tokens.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
        }

        # Act
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "securepass123"},
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


def test_register_email_already_exists(client: TestClient) -> None:
    """Test registration with existing email.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch("app.routers.auth.get_user_by_email") as mock_get_user:
        mock_user = AsyncMock(spec=User)
        mock_user.email = "existing@example.com"
        mock_get_user.return_value = mock_user

        # Act
        response = client.post(
            "/api/auth/register",
            json={"email": "existing@example.com", "password": "securepass123"},
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already registered"


def test_login_success(client: TestClient) -> None:
    """Test successful user login.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch("app.routers.auth.authenticate_user") as mock_auth, patch(
        "app.routers.auth.create_user_tokens"
    ) as mock_tokens:
        mock_user = AsyncMock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user

        mock_tokens.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
        }

        # Act
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "securepass123"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient) -> None:
    """Test login with invalid credentials.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch("app.routers.auth.authenticate_user", return_value=None):
        # Act
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"


def test_get_current_user_success(client: TestClient) -> None:
    """Test getting current user with valid token.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch("app.dependencies.decode_token") as mock_decode, patch(
        "app.dependencies.get_user_by_id"
    ) as mock_get_user:
        # Setup token decoding
        mock_decode.return_value = {"sub": "1", "type": "access", "exp": 9999999999}

        # Setup user retrieval
        mock_user = AsyncMock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.created_at = "2025-01-01T00:00:00Z"
        mock_user.updated_at = "2025-01-01T00:00:00Z"
        mock_get_user.return_value = mock_user

        # Act
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer valid_token"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["id"] == 1


def test_get_current_user_invalid_token(client: TestClient) -> None:
    """Test getting current user with invalid token.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch("app.dependencies.decode_token", side_effect=Exception("Invalid token")):
        # Act
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_no_token(client: TestClient) -> None:
    """Test getting current user without token.

    Args:
        client: FastAPI test client.
    """
    # Act
    response = client.get("/api/auth/me")

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_register_invalid_email(client: TestClient) -> None:
    """Test registration with invalid email format.

    Args:
        client: FastAPI test client.
    """
    # Act
    response = client.post(
        "/api/auth/register",
        json={"email": "invalid-email", "password": "securepass123"},
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_missing_fields(client: TestClient) -> None:
    """Test login with missing fields.

    Args:
        client: FastAPI test client.
    """
    # Act
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com"},  # Missing password
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
