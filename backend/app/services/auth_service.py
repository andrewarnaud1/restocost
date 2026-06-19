"""Authentication service with business logic."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email address.

    Args:
        db: Database session.
        email: User email address.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Get user by ID.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user.

    Args:
        db: Database session.
        user_data: User creation data with email and password.

    Returns:
        Created User object.
    """
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Authenticate user with email and password.

    Args:
        db: Database session.
        email: User email address.
        password: Plain text password.

    Returns:
        User object if authentication successful, None otherwise.
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user_tokens(user_id: int) -> TokenResponse:
    """Create access and refresh tokens for a user.

    Args:
        user_id: User ID to encode in tokens.

    Returns:
        TokenResponse with access and refresh tokens.
    """
    access_token = create_access_token(data={"sub": str(user_id)})
    refresh_token = create_refresh_token(data={"sub": str(user_id)})
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
