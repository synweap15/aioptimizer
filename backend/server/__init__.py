from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from settings import (
    RELEASE_STAGE,
    FRONTEND_URL,
    API_TITLE,
    API_VERSION,
)


def create_server(lifespan: Optional[asynccontextmanager] = None) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        lifespan: Optional async context manager for startup/shutdown events

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # Disable docs in production
    docs_url = "/docs" if RELEASE_STAGE != "production" else None
    redoc_url = None  # Disable ReDoc

    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        debug=RELEASE_STAGE == "local",
        docs_url=docs_url,
        redoc_url=redoc_url,
        lifespan=lifespan,
    )

    # Configure CORS
    origins = [FRONTEND_URL]

    if RELEASE_STAGE == "local":
        # Allow additional origins in local development
        origins.extend([
            "http://localhost:3000",
            "http://localhost:8000",
        ])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
