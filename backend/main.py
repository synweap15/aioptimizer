import uvicorn
from contextlib import asynccontextmanager
from server import create_server
from routers import api, user
from models import init_db, close_db


@asynccontextmanager
async def lifespan(app):
    """
    Async context manager for FastAPI lifespan events.
    Handles startup and shutdown of database connections.
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = create_server(lifespan=lifespan)

# Include API routers
app.include_router(api.router)
app.include_router(user.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
