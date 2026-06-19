"""Create database tables manually."""

import asyncio

from app.db.database import Base, engine
from app.models.user import User  # noqa: F401


async def create_tables():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
