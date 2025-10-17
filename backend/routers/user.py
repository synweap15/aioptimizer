from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from services.user_service import UserService
from dependencies import get_user_service
from schemas.request.user import UserCreateRequest, UserUpdateRequest
from schemas.response.user import UserResponse, UserListResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "",
    response_model=UserListResponse,
    name="List Users",
    status_code=status.HTTP_200_OK,
)
async def list_users(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    user_service: UserService = Depends(get_user_service),
):
    """
    Get a paginated list of all users.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-100)
    """
    users = await user_service.get_all(skip=skip, limit=limit)
    total = await user_service.count()

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    name="Get User",
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """
    Get a specific user by ID.

    - **user_id**: The ID of the user to retrieve
    """
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return UserResponse.model_validate(user)


@router.post(
    "",
    response_model=UserResponse,
    name="Create User",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a new user.

    - **email**: User email address (must be unique)
    - **password**: User password (minimum 8 characters)
    - **full_name**: Optional full name
    """
    user = await user_service.create(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    name="Update User",
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Update user information.

    - **user_id**: The ID of the user to update
    - **email**: New email address (optional)
    - **full_name**: New full name (optional)
    - **is_active**: New active status (optional)
    """
    user = await user_service.update(
        user_id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=user_data.is_active,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    name="Delete User",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete a user.

    - **user_id**: The ID of the user to delete
    """
    deleted = await user_service.delete(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return None
