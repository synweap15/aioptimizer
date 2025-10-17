from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from settings import DATABASE_URL, RELEASE_STAGE

# Convert sync DATABASE_URL to async (replace mysql+pymysql with mysql+aiomysql)
ASYNC_DATABASE_URL = DATABASE_URL.replace("mysql+pymysql://", "mysql+aiomysql://")

# Create async SQLAlchemy engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=RELEASE_STAGE == "local",  # Enable SQL logging in local development
    pool_pre_ping=True,  # Verify connections before using
    pool_size=24,
    max_overflow=48,
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create async session factory
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Important for async
    autocommit=False,
    autoflush=False,
)

# Base class for models (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass


# Lifecycle events
async def init_db():
    """Initialize database connection on startup"""
    async with async_engine.begin() as conn:
        # Create tables if they don't exist (use Alembic in production)
        # await conn.run_sync(Base.metadata.create_all)
        pass


async def close_db():
    """Close database connection on shutdown"""
    await async_engine.dispose()
