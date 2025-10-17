from typing import Optional
from pydantic import EmailStr, Field
from schemas.base import BaseSchema


class UserCreateRequest(BaseSchema):
    """Schema for creating a new user"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: Optional[str] = Field(None, max_length=255, description="User full name")


class UserUpdateRequest(BaseSchema):
    """Schema for updating user information"""

    email: Optional[EmailStr] = Field(None, description="New email address")
    full_name: Optional[str] = Field(None, max_length=255, description="New full name")
    is_active: Optional[bool] = Field(None, description="Account active status")


class UserLoginRequest(BaseSchema):
    """Schema for user login"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
