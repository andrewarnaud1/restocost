#!/usr/bin/env python3
"""CLI script to create a super administrator user.

This script should be run once during initial setup to create the first
administrator account. The admin can then create other users via the API.

⚠️  SECURITY NOTE:
This script should ONLY be run by system administrators with server access.
Never expose this script via a web interface or public API.

📖 Documentation:
See docs/USER_MANAGEMENT.md for complete user management guide.

Usage:
    # Interactive mode (recommended - passwords not in shell history)
    python create_admin.py

    # Command line mode (use only in secure environments)
    python create_admin.py --email admin@example.com --password MySecurePass123

Examples:
    # Local development
    python create_admin.py

    # Docker container
    docker exec -it restocost-backend python create_admin.py

    # Production server (via SSH)
    ssh user@server.com
    cd /var/www/restocost/backend
    python create_admin.py
"""

import asyncio
import sys
from getpass import getpass

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.database import Base, async_session_maker, engine
from app.models.user import User


async def create_admin_user(email: str, password: str) -> None:
    """Create a super admin user.

    Args:
        email: Admin email address.
        password: Admin password (will be hashed).
    """
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"❌ Error: User with email '{email}' already exists.")
            if existing_user.role == "admin":
                print("   This user is already an admin.")
            else:
                print(f"   This user has role: {existing_user.role}")
            sys.exit(1)

        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            hashed_password=hashed_password,
            role="admin",
            must_change_password=False,
        )

        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        print("✅ Super admin user created successfully!")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        print(f"   ID: {admin_user.id}")
        print()
        print("You can now log in with these credentials:")
        print("   curl -X POST http://localhost:8000/api/auth/login \\")
        print("     -H 'Content-Type: application/json' \\")
        print(f"     -d '{{\"email\": \"{email}\", \"password\": \"YOUR_PASSWORD\"}}'")


def main() -> None:
    """Main entry point for the CLI script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create a super administrator user for RestoCost"
    )
    parser.add_argument(
        "--email",
        type=str,
        help="Admin email address (will prompt if not provided)",
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Admin password (will prompt securely if not provided)",
    )

    args = parser.parse_args()

    # Get email
    if args.email:
        email = args.email
    else:
        email = input("Admin email: ").strip()
        if not email:
            print("❌ Error: Email cannot be empty")
            sys.exit(1)

    # Get password
    if args.password:
        password = args.password
        print("⚠️  Warning: Passing password via command line is insecure!")
    else:
        password = getpass("Admin password: ")
        password_confirm = getpass("Confirm password: ")

        if password != password_confirm:
            print("❌ Error: Passwords do not match")
            sys.exit(1)

        if len(password) < 8:
            print("❌ Error: Password must be at least 8 characters")
            sys.exit(1)

    # Create admin
    print()
    print("Creating super admin user...")
    asyncio.run(create_admin_user(email, password))


if __name__ == "__main__":
    main()
