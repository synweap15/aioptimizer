from fastapi import APIRouter, status, HTTPException
from pydantic import HttpUrl, BaseModel, Field
from services.page_fetcher_service import PageFetcherService

router = APIRouter(
    prefix="/page-fetcher",
    tags=["page-fetcher"],
)


class PageFetchRequest(BaseModel):
    """Request schema for page fetching"""

    url: HttpUrl = Field(..., description="URL of the page to fetch")


class PageFetchResponse(BaseModel):
    """Response schema for page fetching"""

    url: str = Field(..., description="URL that was fetched")
    content: str = Field(..., description="Plain text content of the page")
    status: str = Field(..., description="Status of the fetch operation")


@router.post(
    "",
    name="Fetch Page Content",
    response_model=PageFetchResponse,
    status_code=status.HTTP_200_OK,
)
async def fetch_page(request: PageFetchRequest):
    """
    Fetch plain text content from a web page using AI agent.

    **Request Body:**
    - `url`: URL of the page to fetch

    **Response:**
    - `url`: The fetched URL
    - `content`: Plain text content of the page
    - `status`: Operation status
    """
    service = PageFetcherService()

    try:
        result = await service.fetch_page(str(request.url))
        return PageFetchResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch page: {str(e)}",
        )


@router.get(
    "/health",
    name="Page Fetcher Service Health",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """Check if page fetcher service is properly configured"""
    from settings import OPENAI_API_KEY

    return {
        "status": "healthy",
        "openai_configured": bool(OPENAI_API_KEY),
    }
