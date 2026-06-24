"""
backend/routers/analytics.py - Routing configuration for all analytics endpoints.
"""

from typing import List, Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from utils.filters import FilterParams, get_filters
from schemas.analytics import (
    OverviewMetricsResponse,
    RatingTrendPoint,
    BranchPerformanceResponse,
    ComplaintsAnalyticsResponse,
    DistributionsResponse
)
import services.analytics as analytics_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewMetricsResponse)
def get_overview_metrics(
    filters: FilterParams = Depends(get_filters),
    db: Session = Depends(get_db)
):
    """Calculates general KPIs (totals, averages, complaint counts and rate) with filters."""
    return analytics_service.get_overview_metrics(db, filters)


@router.get("/rating-trend", response_model=List[RatingTrendPoint])
def get_rating_trend(
    interval: Literal["daily", "weekly", "monthly"] = Query(
        "weekly", 
        description="Bucket size: daily, weekly, or monthly"
    ),
    filters: FilterParams = Depends(get_filters),
    db: Session = Depends(get_db)
):
    """Calculates weekly/monthly average rating trend with filters."""
    return analytics_service.get_rating_trend(db, filters, interval)


@router.get("/branch-performance", response_model=List[BranchPerformanceResponse])
def get_branch_performance(
    filters: FilterParams = Depends(get_filters),
    db: Session = Depends(get_db)
):
    """Retrieves ranked branch performances sorted by average rating descending."""
    return analytics_service.get_branch_performance(db, filters)


@router.get("/complaints", response_model=ComplaintsAnalyticsResponse)
def get_complaints_analytics(
    filters: FilterParams = Depends(get_filters),
    db: Session = Depends(get_db)
):
    """Retrieves count distributions for the 8 complaint categories using keyword heuristics."""
    return analytics_service.get_complaints_heuristics(db, filters)


@router.get("/distributions", response_model=DistributionsResponse)
def get_distributions_analytics(
    filters: FilterParams = Depends(get_filters),
    db: Session = Depends(get_db)
):
    """Retrieves rating histograms, service type splits, and ordered cuisine splits."""
    return analytics_service.get_distributions(db, filters)
