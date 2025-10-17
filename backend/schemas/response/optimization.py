from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field
from schemas.base import BaseSchema


class OptimizationStatus(BaseSchema):
    """Schema for optimization status updates (SSE)"""

    status: str = Field(..., description="Current status: pending, analyzing, optimizing, completed, failed")
    message: str = Field(..., description="Status message")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage (0-100)")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class OptimizationResult(BaseSchema):
    """Schema for final optimization result"""

    id: str = Field(..., description="Optimization task ID")
    url: str = Field(..., description="Target URL")
    keywords: List[str] = Field(..., description="Target keywords")
    location: str = Field(..., description="Geographic location")

    # Analysis results
    current_rankings: Optional[Dict[str, int]] = Field(
        None, description="Current keyword rankings"
    )
    competitors: Optional[List[str]] = Field(
        None, description="Top competitor URLs"
    )

    # Optimization recommendations
    recommendations: List[str] = Field(
        default_factory=list, description="SEO optimization recommendations"
    )

    # Metadata
    status: str = Field(..., description="Final status")
    created_at: datetime = Field(..., description="Task creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
