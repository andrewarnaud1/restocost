"""SQLAdmin configuration for RestoCost.

This module sets up the admin interface using SQLAdmin, providing
a web-based admin panel for managing database models.

Features:
- User management (CRUD operations)
- Authentication middleware (admin-only access)
- Custom views and actions
- Async SQLAlchemy support

Usage:
    The admin panel is mounted at /admin and requires admin authentication.
    Access it at: http://localhost:8000/admin
"""

from typing import Optional

from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.config import get_settings
from app.core.security import verify_password
from app.db.database import async_session_maker, engine
from app.models.user import User
from app.services.auth_service import get_user_by_email

settings = get_settings()


class AdminAuth(AuthenticationBackend):
    """Authentication backend for admin panel.

    Only users with 'admin' role can access the admin panel.
    Uses JWT-based session management.
    """

    async def login(self, request: Request) -> bool:
        """Authenticate admin user.

        Args:
            request: Starlette request object containing form data.

        Returns:
            bool: True if authentication successful, False otherwise.
        """
        form = await request.form()
        email = form.get("username")  # SQLAdmin uses 'username' field
        password = form.get("password")

        if not email or not password:
            return False

        # Get user from database
        async with async_session_maker() as session:
            user = await get_user_by_email(session, str(email))

            if not user:
                return False

            # Verify password
            if not verify_password(str(password), user.hashed_password):
                return False

            # Check if user is admin
            if user.role != "admin":
                return False

            # Store user ID in session
            request.session.update({"user_id": user.id, "role": user.role})
            return True

    async def logout(self, request: Request) -> bool:
        """Logout admin user.

        Args:
            request: Starlette request object.

        Returns:
            bool: Always returns True.
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        """Check if user is authenticated.

        Args:
            request: Starlette request object.

        Returns:
            Optional[RedirectResponse]: None if authenticated, redirect otherwise.
        """
        user_id = request.session.get("user_id")
        role = request.session.get("role")

        if not user_id or role != "admin":
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        return None


class UserAdmin(ModelView, model=User):
    """Admin view for User model.

    Provides CRUD operations for users with custom display options.
    """

    # Metadata
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    # List view columns
    column_list = [
        User.id,
        User.email,
        User.role,
        User.must_change_password,
        User.created_at,
    ]

    # Searchable columns
    column_searchable_list = [User.email]

    # Sortable columns
    column_sortable_list = [User.id, User.email, User.role, User.created_at]

    # Default sort
    column_default_sort = [(User.created_at, True)]  # Descending

    # Detail view columns
    column_details_list = [
        User.id,
        User.email,
        User.role,
        User.must_change_password,
        User.created_at,
        User.updated_at,
    ]

    # Excluded form columns (can't use both form_columns and form_excluded_columns)
    form_excluded_columns = [
        User.id,
        User.hashed_password,
        User.created_at,
        User.updated_at,
    ]

    # Column labels
    column_labels = {
        User.id: "ID",
        User.email: "Email",
        User.role: "Role",
        User.must_change_password: "Must Change Password",
        User.created_at: "Created At",
        User.updated_at: "Updated At",
    }

    # Column formatters
    column_formatters = {
        User.must_change_password: lambda m, a: "Yes" if m.must_change_password else "No",
        User.role: lambda m, a: m.role.upper(),
    }

    # Pagination
    page_size = 20
    page_size_options = [10, 20, 50, 100]

    # Can export
    can_export = True

    # Export types
    export_types = ["csv", "json"]


def create_admin(app) -> Admin:
    """Create and configure SQLAdmin instance.

    Args:
        app: FastAPI application instance.

    Returns:
        Admin: Configured SQLAdmin instance.

    Example:
        ```python
        from fastapi import FastAPI
        from app.admin import create_admin

        app = FastAPI()
        admin = create_admin(app)
        ```
    """
    # Create authentication backend
    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

    # Create admin instance
    admin = Admin(
        app=app,
        engine=engine,
        title="RestoCost Admin",
        logo_url=None,  # Add your logo URL here
        authentication_backend=authentication_backend,
        session_maker=async_session_maker,
    )

    # Register model views
    admin.add_view(UserAdmin)

    return admin
