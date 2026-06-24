"""
backend/schemas/ai.py - Pydantic models for AI Request/Response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date


class AIInsightsRequest(BaseModel):
    """Filter parameters passed in the request body for AI insights."""
    city_id: Optional[int] = Field(None, description="Filter by City ID")
    branch_id: Optional[int] = Field(None, description="Filter by Branch ID")
    brand_id: Optional[int] = Field(None, description="Filter by Brand ID")
    ordered_cuisine: Optional[str] = Field(None, description="Filter by cuisine reviewed ('Indian', 'Thai', 'Italian', 'Chinese', 'Fast Food')")
    service_type: Optional[Literal["delivery", "dine-in", "takeaway"]] = Field(None, description="Filter by service channel")
    price_segment: Optional[Literal["budget", "mid-range", "premium"]] = Field(None, description="Filter by pricing tier")
    min_rating: Optional[int] = Field(None, ge=1, le=5, description="Min rating filter (1-5)")
    max_rating: Optional[int] = Field(None, ge=1, le=5, description="Max rating filter (1-5)")
    start_date: Optional[date] = Field(None, description="Filter start date (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="Filter end date (YYYY-MM-DD)")


class AIInsightsResponse(BaseModel):
    """Response structure for executive diagnostics."""
    summary: str = Field(..., description="Executive brief of current operation metrics")
    priority_level: Literal["low", "medium", "high", "critical"] = Field(..., description="Priority severity assignment")
    root_causes: List[str] = Field(..., description="Parsed bottleneck causes")
    recommendations: List[str] = Field(..., description="Actionable solutions")


class AIResponseRequest(BaseModel):
    """Input parameters for drafting a customer response."""
    review_text: str = Field(..., min_length=5, description="Customer review text")
    rating: int = Field(..., ge=1, le=5, description="Customer rating (1-5)")


class AIResponseResponse(BaseModel):
    """Response structure containing the drafted response."""
    response: str = Field(..., description="Empathetic, professional guest relation reply draft")
