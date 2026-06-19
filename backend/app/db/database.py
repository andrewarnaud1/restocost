"""Database configuration and session management.

This module contains all database-related setup:
- SQLAlchemy Base for ORM models
- Async engine configuration
- Async session factory
- Database health check utility
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def check_db_connection() -> bool:
    """Check if database connection is healthy.

    Returns:
        bool: True if database is reachable, False otherwise.

    Example:
        ```python
        is_healthy = await check_db_connection()
        if not is_healthy:
            raise HTTPException(status_code=503, detail="Database unavailable")
        ```
    """
    try:
        async with async_session_maker() as session:
            from sqlalchemy import text

            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
