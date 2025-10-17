from fastapi import APIRouter, status

router = APIRouter(
    prefix="/api",
    tags=["api"],
)


@router.get(
    "/health",
    name="Health Check",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy", "message": "API is running"}
