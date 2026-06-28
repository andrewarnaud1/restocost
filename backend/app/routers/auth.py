"""Authentication endpoints for user registration and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import verify_password
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.user import (
    ChangePasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    change_password,
    create_user_tokens,
)

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new user.

    Public registration is disabled. All users must be created by an administrator.

    Args:
        user_data: User registration data with email and password.
        db: Database session.

    Returns:
        TokenResponse with access and refresh tokens.

    Raises:
        HTTPException: 403 - Registration is always disabled.

    Note:
        This endpoint is kept for API compatibility but always returns 403.
        Users must be created via /api/admin/users by an administrator.
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "Public registration is disabled. "
            "Please contact an administrator to create an account for you."
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user and return JWT tokens.

    Args:
        credentials: User login credentials with email and password.
        db: Database session.

    Returns:
        TokenResponse with access and refresh tokens.

    Raises:
        HTTPException: 401 if credentials are invalid.

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/auth/login \\
          -H "Content-Type: application/json" \\
          -d '{"email": "user@example.com", "password": "securepass123"}'
        ```
    """
    user = await authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate tokens
    tokens = create_user_tokens(user.id)
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user from JWT token.

    Returns:
        UserResponse with user information (without password).

    Raises:
        HTTPException: 401 if token is invalid or expired.

    Example:
        ```bash
        curl -X GET http://localhost:8000/api/auth/me \\
          -H "Authorization: Bearer <your_access_token>"
        ```
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password", response_model=UserResponse)
async def change_user_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Change current user's password.

    Users with must_change_password=True must use this endpoint before
    accessing other protected resources.

    Args:
        password_data: Current and new password.
        current_user: Current authenticated user from JWT token.
        db: Database session.

    Returns:
        UserResponse with updated user information.

    Raises:
        HTTPException: 400 if current password is incorrect.

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/auth/change-password \\
          -H "Authorization: Bearer <your_access_token>" \\
          -H "Content-Type: application/json" \\
          -d '{
            "current_password": "TempPass123",
            "new_password": "MyNewSecurePass456"
          }'
        ```
    """
    # Verify current password
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Change password
    updated_user = await change_password(db, current_user, password_data.new_password)

    return UserResponse.model_validate(updated_user)
