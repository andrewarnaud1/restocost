"""Authentication endpoints for user registration and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.auth_service import (
    authenticate_user,
    create_user,
    create_user_tokens,
    get_user_by_email,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new user.

    Args:
        user_data: User registration data with email and password.
        db: Database session.

    Returns:
        TokenResponse with access and refresh tokens.

    Raises:
        HTTPException: 400 if email already registered.

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/auth/register \\
          -H "Content-Type: application/json" \\
          -d '{"email": "user@example.com", "password": "securepass123"}'
        ```
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = await create_user(db, user_data)

    # Generate tokens
    tokens = create_user_tokens(user.id)
    return tokens


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
