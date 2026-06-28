"""Admin endpoints for user management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_admin, get_db
from app.models.user import User
from app.schemas.user import AdminUserCreate, AdminUserCreateResponse
from app.services.auth_service import create_user_by_admin, get_user_by_email

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post(
    "/users",
    response_model=AdminUserCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_as_admin(
    user_data: AdminUserCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> AdminUserCreateResponse:
    """Create a new user with a temporary password (admin only).

    Only users with 'owner' role can create new users. The created user
    will receive a temporary password and must change it on first login.

    Args:
        user_data: User creation data with email and role.
        db: Database session.
        admin: Current authenticated admin user.

    Returns:
        AdminUserCreateResponse with user info and temporary password.

    Raises:
        HTTPException: 400 if email already exists.
        HTTPException: 403 if user is not an admin.

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/admin/users \\
          -H "Authorization: Bearer <admin_access_token>" \\
          -H "Content-Type: application/json" \\
          -d '{
            "email": "chef@restaurant.com",
            "role": "staff"
          }'
        ```

    Response example:
        ```json
        {
          "id": 2,
          "email": "chef@restaurant.com",
          "role": "staff",
          "temporary_password": "Abc123XyZ456",
          "must_change_password": true
        }
        ```

    Usage:
        1. Admin calls this endpoint to create a user
        2. Admin shares email and temporary_password with the new user
           (in person, via WhatsApp, SMS, etc.)
        3. New user logs in with temporary password
        4. New user changes password via POST /api/auth/change-password
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user with temporary password
    user, temp_password = await create_user_by_admin(db, user_data)

    return AdminUserCreateResponse(
        id=user.id,
        email=user.email,
        role=user.role,  # type: ignore[arg-type]
        temporary_password=temp_password,
        must_change_password=user.must_change_password,
    )
