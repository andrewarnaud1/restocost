"""Centralized dependencies for dependency injection.

This module contains all reusable dependencies that can be injected
into FastAPI path operations using Depends().
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session_maker


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
