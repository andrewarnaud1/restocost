"""Tests for authentication endpoints."""

from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from app.models.user import User


def test_register_always_disabled(client: TestClient) -> None:
    """Test that public registration is always disabled.

    Args:
        client: FastAPI test client.
    """
    # Act
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "securepass123"},
    )

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Public registration is disabled" in response.json()["detail"]


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
        mock_user.role = "staff"  # Add role for validation
        mock_user.must_change_password = False
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
        assert data["role"] == "staff"


def test_get_current_user_invalid_token(client: TestClient) -> None:
    """Test getting current user with invalid token.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    import jwt

    with patch(
        "app.dependencies.decode_token",
        side_effect=jwt.InvalidTokenError("Invalid token"),
    ):
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

    # Assert - HTTPBearer returns 401 when no credentials provided
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


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
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_change_password_success(client: TestClient) -> None:
    """Test successful password change.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch("app.dependencies.decode_token") as mock_decode, patch(
        "app.dependencies.get_user_by_id"
    ) as mock_get_user, patch(
        "app.routers.auth.verify_password", return_value=True
    ), patch(
        "app.routers.auth.change_password"
    ) as mock_change:
        # Setup current user
        mock_user = AsyncMock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = "staff"
        mock_user.hashed_password = "hashed_old_password"
        mock_user.must_change_password = True
        mock_user.created_at = "2025-01-01T00:00:00Z"
        mock_user.updated_at = "2025-01-01T00:00:00Z"

        mock_decode.return_value = {"sub": "1", "type": "access", "exp": 9999999999}
        mock_get_user.return_value = mock_user

        # Setup updated user
        updated_user = AsyncMock(spec=User)
        updated_user.id = 1
        updated_user.email = "test@example.com"
        updated_user.role = "staff"
        updated_user.must_change_password = False
        updated_user.created_at = "2025-01-01T00:00:00Z"
        updated_user.updated_at = "2025-01-01T00:00:00Z"
        mock_change.return_value = updated_user

        # Act
        response = client.post(
            "/api/auth/change-password",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "current_password": "old_password",
                "new_password": "new_password123",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["must_change_password"] is False


def test_change_password_incorrect_current(client: TestClient) -> None:
    """Test password change with incorrect current password.

    Args:
        client: FastAPI test client.
    """
    # Arrange
    with patch("app.dependencies.decode_token") as mock_decode, patch(
        "app.dependencies.get_user_by_id"
    ) as mock_get_user, patch("app.routers.auth.verify_password", return_value=False):
        # Setup current user
        mock_user = AsyncMock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = "staff"
        mock_user.hashed_password = "hashed_old_password"

        mock_decode.return_value = {"sub": "1", "type": "access", "exp": 9999999999}
        mock_get_user.return_value = mock_user

        # Act
        response = client.post(
            "/api/auth/change-password",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "current_password": "wrong_password",
                "new_password": "new_password123",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Current password is incorrect"
