"""User Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

# Type alias for user roles
UserRole = Literal["admin", "owner", "staff"]


class UserBase(BaseModel):
    """Base user schema with common attributes."""

    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration request."""

    password: str


class UserLogin(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (without password)."""

    id: int
    role: UserRole
    must_change_password: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserCreate(BaseModel):
    """Schema for admin creating a user."""

    email: EmailStr
    role: UserRole = "staff"


class AdminUserCreateResponse(BaseModel):
    """Schema for response when admin creates a user."""

    id: int
    email: EmailStr
    role: UserRole
    temporary_password: str
    must_change_password: bool

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    """Schema for changing password."""

    current_password: str
    new_password: str


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    sub: int  # User ID
    exp: int  # Expiration timestamp
    type: str  # Token type: "access" or "refresh"
