from typing import AsyncIterator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import async_session_maker


async def get_db() -> AsyncIterator[AsyncSession]:
    """
    Async database session dependency for FastAPI routes.

    Usage:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Service Dependencies
def get_user_service(db: AsyncSession = Depends(get_db)):
    """
    Dependency injection for UserService.

    Usage:
        @router.get("/users/{user_id}")
        async def get_user(
            user_id: int,
            user_service: UserService = Depends(get_user_service)
        ):
            return await user_service.get_by_id(user_id)
    """
    from services.user_service import UserService

    return UserService(db)
