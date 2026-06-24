"""
backend/schemas/analytics.py - Pydantic models for analytics responses.
"""

from datetime import date
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class OverviewMetricsResponse(BaseModel):
    """Schema for GET /api/analytics/overview"""
    total_reviews: int = Field(..., description="Total count of customer reviews matching filters")
    avg_rating: Optional[float] = Field(None, description="Average rating matching filters")
    avg_wait_time: Optional[float] = Field(None, description="Average customer wait time in minutes")
    positive_review_count: int = Field(..., description="Count of reviews with rating >= 4")
    neutral_review_count: int = Field(..., description="Count of reviews with rating = 3")
    negative_review_count: int = Field(..., description="Count of reviews with rating <= 2")
    complaint_rate: float = Field(..., description="Proportion of negative reviews (negative_reviews / total_reviews)")

    class Config:
        from_attributes = True


class RatingTrendPoint(BaseModel):
    """Single point in the rating trend time series"""
    time_bucket: str = Field(..., description="Aggregated date string (daily, weekly, or monthly)")
    avg_rating: Optional[float] = Field(None, description="Average rating in this time bucket")


class BranchPerformanceResponse(BaseModel):
    """Schema for GET /api/analytics/branch-performance element"""
    branch_name: str = Field(..., description="Name of the restaurant branch")
    brand_name: str = Field(..., description="Name of the brand")
    city: str = Field(..., description="Name of the city")
    avg_rating: Optional[float] = Field(None, description="Average rating of this branch")
    review_count: int = Field(..., description="Total count of reviews for this branch")
    avg_wait_time: Optional[float] = Field(None, description="Average wait time in minutes")


class ComplaintsAnalyticsResponse(BaseModel):
    """Schema for GET /api/analytics/complaints"""
    delivery_delay: int = Field(0, description="Heuristics keyword count for delivery delay issues")
    food_quality: int = Field(0, description="Heuristics keyword count for food quality issues")
    pricing: int = Field(0, description="Heuristics keyword count for pricing issues")
    packaging: int = Field(0, description="Heuristics keyword count for packaging issues")
    hygiene: int = Field(0, description="Heuristics keyword count for hygiene issues")
    staff_behavior: int = Field(0, description="Heuristics keyword count for staff behavior issues")
    ambience: int = Field(0, description="Heuristics keyword count for ambience issues")
    portion_size: int = Field(0, description="Heuristics keyword count for portion size issues")


class DistributionsResponse(BaseModel):
    """Schema for GET /api/analytics/distributions"""
    rating_histogram: Dict[int, int] = Field(..., description="Count of reviews per rating value (1 to 5)")
    service_type_distribution: Dict[str, int] = Field(..., description="Count of reviews per service type")
    cuisine_distribution: Dict[str, int] = Field(..., description="Count of reviews per cuisine actually ordered")
