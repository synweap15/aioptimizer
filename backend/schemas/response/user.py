from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field
from schemas.base import BaseSchema


class UserResponse(BaseSchema):
    """Schema for user response (excludes sensitive data)"""

    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")
    is_active: bool = Field(..., description="Whether user account is active")
    is_superuser: bool = Field(..., description="Whether user has superuser privileges")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserListResponse(BaseSchema):
    """Schema for paginated user list response"""

    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")


class UserLoginResponse(BaseSchema):
    """Schema for login response"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user information")
