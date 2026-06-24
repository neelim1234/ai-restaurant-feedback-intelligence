"""
backend/utils/filters.py - Reusable SQL query filter builder and query schema.
"""

from datetime import date
from typing import Optional, Set, Tuple, Type
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy.orm import Query as SQLQuery

from models.feedback import Feedback, FeedbackAnalysis
from models.org import Branch


class FilterParams(BaseModel):
    """Container for all supported API filters."""
    city_id: Optional[int] = None
    branch_id: Optional[int] = None
    brand_id: Optional[int] = None
    ordered_cuisine: Optional[str] = None
    service_type: Optional[str] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    price_segment: Optional[str] = None
    sentiment: Optional[str] = None


def get_filters(
    city_id: Optional[int] = Query(None, description="Filter by City ID"),
    branch_id: Optional[int] = Query(None, description="Filter by Branch ID"),
    brand_id: Optional[int] = Query(None, description="Filter by Brand ID"),
    ordered_cuisine: Optional[str] = Query(None, description="Filter by cuisine actually ordered"),
    service_type: Optional[str] = Query(None, description="Filter by service type (delivery, dine-in, takeaway)"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum rating (1-5)"),
    max_rating: Optional[int] = Query(None, ge=1, le=5, description="Maximum rating (1-5)"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    price_segment: Optional[str] = Query(None, description="Filter by price segment (budget, mid-range, premium)"),
    sentiment: Optional[str] = Query(None, description="Filter by pre-analyzed sentiment (positive, neutral, negative)"),
) -> FilterParams:
    """FastAPI Dependency to parse and group filter query parameters."""
    return FilterParams(
        city_id=city_id,
        branch_id=branch_id,
        brand_id=brand_id,
        ordered_cuisine=ordered_cuisine,
        service_type=service_type,
        min_rating=min_rating,
        max_rating=max_rating,
        start_date=start_date,
        end_date=end_date,
        price_segment=price_segment,
        sentiment=sentiment,
    )


def apply_filters(
    query: SQLQuery, 
    filters: FilterParams, 
    joined_models: Set[Type]
) -> Tuple[SQLQuery, Set[Type]]:
    """
    Applies the FilterParams fields dynamically to a SQLAlchemy query.
    
    Uses joined_models to keep track of already joined tables to prevent
    duplicate join errors. Returns the modified query and updated joined_models set.
    """
    new_joins = set()
    
    def safe_join(model):
        nonlocal query
        if model not in joined_models and model not in new_joins:
            query = query.join(model)
            new_joins.add(model)

    # 1. Location filters
    if filters.city_id is not None:
        safe_join(Branch)
        query = query.filter(Branch.city_id == filters.city_id)
        
    if filters.branch_id is not None:
        query = query.filter(Feedback.branch_id == filters.branch_id)
        
    # 2. Business filters
    if filters.brand_id is not None:
        safe_join(Branch)
        query = query.filter(Branch.brand_id == filters.brand_id)
        
    # 3. Food actually ordered filter
    if filters.ordered_cuisine is not None:
        query = query.filter(Feedback.ordered_cuisine == filters.ordered_cuisine)
        
    # 4. Service filter
    if filters.service_type is not None:
        query = query.filter(Feedback.service_type == filters.service_type)
        
    # 5. Price segment filter
    if filters.price_segment is not None:
        query = query.filter(Feedback.price_segment == filters.price_segment)
        
    # 6. Rating filters
    if filters.min_rating is not None:
        query = query.filter(Feedback.rating >= filters.min_rating)
        
    if filters.max_rating is not None:
        query = query.filter(Feedback.rating <= filters.max_rating)
        
    # 7. Time range filters
    if filters.start_date is not None:
        query = query.filter(Feedback.feedback_date >= filters.start_date)
        
    if filters.end_date is not None:
        query = query.filter(Feedback.feedback_date <= filters.end_date)
        
    # 8. Sentiment filter (requires joining feedback_analysis)
    if filters.sentiment is not None:
        if FeedbackAnalysis not in joined_models and FeedbackAnalysis not in new_joins:
            query = query.join(FeedbackAnalysis, FeedbackAnalysis.feedback_id == Feedback.id)
            new_joins.add(FeedbackAnalysis)
        query = query.filter(FeedbackAnalysis.sentiment == filters.sentiment)
        
    return query, joined_models.union(new_joins)

