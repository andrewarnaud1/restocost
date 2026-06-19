"""RestoCost CLI - Command Line Interface for database and user management.

This CLI provides commands for managing the RestoCost application:
- Database migrations (Alembic integration)
- User management (create admin, etc.)
- Development server

Usage:
    restocost --help
    restocost db init
    restocost db upgrade
    restocost create-admin
    restocost run
"""

import asyncio
import sys
from getpass import getpass
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.database import Base, async_session_maker, engine
from app.models.user import User

# Create Typer app
app = typer.Typer(
    name="restocost",
    help="RestoCost CLI - Restaurant cost management system",
    add_completion=False,
)

# Create Rich console for beautiful output
console = Console()

# Database commands group
db_app = typer.Typer(help="Database management commands")
app.add_typer(db_app, name="db")


@db_app.command("init")
def db_init() -> None:
    """Initialize the database with Alembic migrations.

    This command creates the initial migration and applies it to the database.
    Run this once when setting up the project for the first time.

    Example:
        restocost db init
    """
    console.print("\n[bold cyan]🔧 Initializing database...[/bold cyan]\n")

    # Check if alembic.ini exists
    alembic_ini = Path("alembic.ini")
    if not alembic_ini.exists():
        console.print(
            "[bold red]❌ Error:[/bold red] alembic.ini not found. "
            "Make sure you're in the backend directory."
        )
        raise typer.Exit(1)

    # Run alembic upgrade head
    import subprocess

    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True,
        )
        console.print(result.stdout)
        console.print(
            "[bold green]✅ Database initialized successfully![/bold green]\n"
        )
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e.stderr}")
        raise typer.Exit(1)


@db_app.command("upgrade")
def db_upgrade() -> None:
    """Apply all pending database migrations.

    This command runs 'alembic upgrade head' to apply all pending migrations
    to the database.

    Example:
        restocost db upgrade
    """
    console.print("\n[bold cyan]⬆️  Upgrading database...[/bold cyan]\n")

    import subprocess

    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True,
        )
        console.print(result.stdout)
        console.print(
            "[bold green]✅ Database upgraded successfully![/bold green]\n"
        )
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e.stderr}")
        raise typer.Exit(1)


@db_app.command("reset")
def db_reset(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    )
) -> None:
    """Reset the database (DROP ALL TABLES and recreate).

    ⚠️  WARNING: This will DELETE ALL DATA in the database!

    This command drops all tables and recreates them using SQLAlchemy models.
    Use with caution, especially in production.

    Example:
        restocost db reset --force
    """
    if not force:
        console.print(
            "\n[bold red]⚠️  WARNING: This will DELETE ALL DATA![/bold red]\n"
        )
        confirm = typer.confirm("Are you sure you want to reset the database?")
        if not confirm:
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit(0)

    console.print("\n[bold cyan]🔄 Resetting database...[/bold cyan]\n")

    async def reset_db() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(reset_db())
    console.print("[bold green]✅ Database reset successfully![/bold green]\n")


@app.command("create-admin")
def create_admin(
    email: Optional[str] = typer.Option(
        None,
        "--email",
        "-e",
        help="Admin email address",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="Admin password (not recommended, use interactive mode)",
    ),
) -> None:
    """Create a super administrator user.

    This command creates a super admin user with full system access.
    The admin can then create other users (owners, staff) via the API.

    Security:
        - Only run this command with server access
        - Never expose this via a web interface
        - Use interactive mode (no --password flag) for better security

    Examples:
        # Interactive mode (recommended)
        restocost create-admin

        # With email prompt
        restocost create-admin --email admin@example.com

        # With both (not recommended)
        restocost create-admin --email admin@example.com --password secret
    """
    console.print(
        Panel.fit(
            "[bold cyan]RestoCost - Create Super Administrator[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()

    # Get email
    if not email:
        email = typer.prompt("📧 Admin email")

    if not email or "@" not in email:
        console.print("[bold red]❌ Error:[/bold red] Invalid email address")
        raise typer.Exit(1)

    # Get password
    if password:
        console.print(
            "[yellow]⚠️  Warning:[/yellow] Passing password via command line "
            "is insecure!"
        )
    else:
        password = getpass("🔑 Admin password: ")
        password_confirm = getpass("🔑 Confirm password: ")

        if password != password_confirm:
            console.print("[bold red]❌ Error:[/bold red] Passwords do not match")
            raise typer.Exit(1)

        if len(password) < 8:
            console.print(
                "[bold red]❌ Error:[/bold red] Password must be at least "
                "8 characters"
            )
            raise typer.Exit(1)

    # Create admin user
    console.print()
    console.print("[bold cyan]Creating super admin user...[/bold cyan]")

    async def create_admin_user() -> None:
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
                console.print(
                    f"\n[bold red]❌ Error:[/bold red] User with email "
                    f"'{email}' already exists."
                )
                if existing_user.role == "admin":
                    console.print("   This user is already an admin.")
                else:
                    console.print(f"   This user has role: {existing_user.role}")
                raise typer.Exit(1)

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

            # Display success message
            console.print()
            console.print(
                Panel.fit(
                    f"[bold green]✅ Super admin user created successfully![/bold green]\n\n"
                    f"[cyan]Email:[/cyan] {admin_user.email}\n"
                    f"[cyan]Role:[/cyan] {admin_user.role}\n"
                    f"[cyan]ID:[/cyan] {admin_user.id}",
                    border_style="green",
                    title="Success",
                )
            )
            console.print()

            # Display login instructions
            table = Table(title="Next Steps", show_header=False, border_style="cyan")
            table.add_row(
                "1️⃣",
                "Start the server: [bold]restocost run[/bold] or "
                "[bold]uvicorn app.main:app --reload[/bold]",
            )
            table.add_row(
                "2️⃣",
                f"Login at: [bold]POST http://localhost:8000/api/auth/login[/bold]",
            )
            table.add_row(
                "3️⃣",
                "Create other users via: [bold]POST /api/admin/users[/bold]",
            )
            console.print(table)
            console.print()

    asyncio.run(create_admin_user())


@app.command("run")
def run_server(
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
        help="Host to bind to",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port to bind to",
    ),
    reload: bool = typer.Option(
        True,
        "--reload/--no-reload",
        help="Enable auto-reload on code changes",
    ),
) -> None:
    """Start the FastAPI development server.

    This command starts the Uvicorn server with the FastAPI application.
    Auto-reload is enabled by default for development.

    Examples:
        # Default (localhost:8000 with reload)
        restocost run

        # Custom host and port
        restocost run --host 127.0.0.1 --port 3000

        # Production mode (no reload)
        restocost run --no-reload
    """
    console.print(
        Panel.fit(
            f"[bold cyan]Starting RestoCost Server[/bold cyan]\n\n"
            f"[cyan]Host:[/cyan] {host}\n"
            f"[cyan]Port:[/cyan] {port}\n"
            f"[cyan]Auto-reload:[/cyan] {reload}",
            border_style="cyan",
        )
    )
    console.print()

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


@app.command("version")
def version() -> None:
    """Display RestoCost version information."""
    from app.core.config import get_settings

    settings = get_settings()

    table = Table(show_header=False, border_style="cyan")
    table.add_row("[cyan]Project:[/cyan]", settings.PROJECT_NAME)
    table.add_row("[cyan]Version:[/cyan]", settings.VERSION)
    table.add_row("[cyan]Environment:[/cyan]", settings.ENVIRONMENT)

    console.print()
    console.print(table)
    console.print()


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
