from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from services.optimization_service import InvestigationService
from schemas.request.optimization import InvestigationRequest

router = APIRouter(
    prefix="/optimize",
    tags=["optimization"],
)


@router.post(
    "",
    name="AIO Investigation",
    status_code=status.HTTP_200_OK,
)
async def investigate_aio(request: InvestigationRequest):
    """
    Run AIO (AI Optimization) investigation for a given URL with keywords and location.

    Streams results via Server-Sent Events (SSE).

    **Request Body:**
    - `url`: Target URL to optimize
    - `keywords`: List of target keywords (1-10)
    - `location`: Geographic location for search
    - `language`: Language code (optional, default: en)

    **Response:** Server-Sent Events stream with optimization progress and results

    **SSE Event Format:**
    ```json
    {
        "status": "pending|analyzing|optimizing|completed|failed",
        "message": "Status message",
        "progress": 0-100,
        "data": { ... }
    }
    ```
    """
    service = InvestigationService()

    async def event_generator():
        """Generate SSE events from investigation service"""
        async for event in service.investigate(
            url=str(request.url),
            keywords=request.keywords,
            location=request.location,
            language=request.language or "en",
        ):
            yield event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering in nginx
        },
    )


@router.get(
    "/health",
    name="Investigation Service Health",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """Check if investigation service is properly configured"""
    from settings import OPENAI_API_KEY, SERPAPI_API_KEY

    return {
        "status": "healthy",
        "openai_configured": bool(OPENAI_API_KEY),
        "serpapi_configured": bool(SERPAPI_API_KEY),
    }
