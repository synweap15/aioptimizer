from typing import Optional, List
from pydantic import Field, HttpUrl
from schemas.base import BaseSchema


class InvestigationRequest(BaseSchema):
    """Schema for SEO optimization request"""

    url: HttpUrl = Field(..., description="Target URL to optimize")
    keywords: List[str] = Field(
        ..., min_length=1, max_length=10, description="Target keywords (1-10)"
    )
    location: str = Field(
        ..., min_length=2, max_length=100, description="Geographic location for search"
    )
    language: Optional[str] = Field(
        default="en", description="Language code (default: en)"
    )
