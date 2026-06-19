"""Centralized dependencies for dependency injection.

This module contains all reusable dependencies that can be injected
into FastAPI path operations using Depends().
"""

from collections.abc import AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.database import async_session_maker
from app.models.user import User
from app.services.auth_service import get_user_by_id

security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Get async database session dependency.

    Yields:
        AsyncSession: The database session.

    Example:
        ```python
        from fastapi import Depends
        from app.dependencies import get_db

        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials.
        db: Database session.

    Returns:
        Current authenticated User object.

    Raises:
        HTTPException: If token is invalid or user not found.

    Example:
        ```python
        from fastapi import Depends
        from app.dependencies import get_current_user
        from app.models.user import User

        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
        ```
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = decode_token(token)

        user_id_str = payload.get("sub")
        token_type = payload.get("type")

        if user_id_str is None or token_type != "access":
            raise credentials_exception

        user_id = int(user_id_str)

    except (jwt.InvalidTokenError, ValueError) as e:
        raise credentials_exception from e

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user
