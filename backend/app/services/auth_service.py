"""Authentication service with business logic."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_temporary_password,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.user import AdminUserCreate, TokenResponse, UserCreate


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


async def count_users(db: AsyncSession) -> int:
    """Count total number of users in database.

    Args:
        db: Database session.

    Returns:
        Total number of users.
    """
    result = await db.execute(select(func.count(User.id)))
    return result.scalar_one()


async def create_user(
    db: AsyncSession, user_data: UserCreate, role: str = "staff"
) -> User:
    """Create a new user.

    Args:
        db: Database session.
        user_data: User creation data with email and password.
        role: User role (owner or staff). Defaults to staff.

    Returns:
        Created User object.
    """
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        role=role,
        must_change_password=False,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_user_by_admin(
    db: AsyncSession, user_data: AdminUserCreate
) -> tuple[User, str]:
    """Create a new user by admin with temporary password.

    Args:
        db: Database session.
        user_data: Admin user creation data with email and role.

    Returns:
        Tuple of (Created User object, temporary password).
    """
    # Generate temporary password
    temp_password = generate_temporary_password()
    hashed_password = get_password_hash(temp_password)

    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        must_change_password=True,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user, temp_password


async def change_password(
    db: AsyncSession, user: User, new_password: str
) -> User:
    """Change user password.

    Args:
        db: Database session.
        user: User object to update.
        new_password: New plain text password.

    Returns:
        Updated User object.
    """
    user.hashed_password = get_password_hash(new_password)
    user.must_change_password = False
    await db.commit()
    await db.refresh(user)
    return user


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
