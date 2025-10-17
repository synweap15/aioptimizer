from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service layer for user operations with dependency injection"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID to fetch

        Returns:
            User object or None if not found
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: Email address to search for

        Returns:
            User object or None if not found
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User objects
        """
        stmt = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """
        Count total number of users.

        Returns:
            Total user count
        """
        stmt = select(func.count(User.id))
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(
        self, email: str, password: str, full_name: Optional[str] = None
    ) -> Optional[User]:
        """
        Create a new user.

        Args:
            email: User email address
            password: Plain text password (will be hashed)
            full_name: Optional full name

        Returns:
            Created User object or None if email already exists
        """
        try:
            hashed_password = pwd_context.hash(password)
            user = User(email=email, hashed_password=hashed_password, full_name=full_name)
            self.db.add(user)
            await self.db.flush()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            return None

    async def update(
        self,
        user_id: int,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[User]:
        """
        Update user information.

        Args:
            user_id: ID of user to update
            email: New email address (optional)
            full_name: New full name (optional)
            is_active: New active status (optional)

        Returns:
            Updated User object or None if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None

        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if is_active is not None:
            user.is_active = is_active

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        """
        Delete a user.

        Args:
            user_id: ID of user to delete

        Returns:
            True if deleted, False if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.flush()
        return True

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to check against

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            email: User email
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = await self.get_by_email(email)
        if not user:
            return None
        if not await self.verify_password(password, user.hashed_password):
            return None
        return user
