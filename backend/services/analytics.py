"""
backend/services/analytics.py - Database operations and SQL aggregates for analytics.
"""

from typing import Dict, Any, List
from sqlalchemy import func, case, or_, cast, String, Date
from sqlalchemy.orm import Session

from models.feedback import Feedback, FeedbackAnalysis
from models.org import Branch, Brand
from models.lookup import City
from utils.filters import FilterParams, apply_filters

# Centralized Keyword Heuristics for Complaint Categories
COMPLAINT_KEYWORDS = {
    "delivery_delay": ["late", "delayed", "slow delivery", "took forever", "waited too long", "late delivery", "delay in", "wait for delivery"],
    "food_quality": ["cold", "stale", "tasteless", "not fresh", "undercooked", "overcooked", "raw", "soggy", "bland", "inedible"],
    "pricing": ["overpriced", "expensive", "not worth", "too costly", "robbery", "unjustified pricing", "rip-off", "terrible price"],
    "packaging": ["terrible packaging", "leaked", "spilled", "damaged box", "damaged container", "crushed", "leaking", "poor packaging"],
    "hygiene": ["hair in", "smelled off", "contamination", "unhygienic", "dirty premises", "not safe to eat", "filthy", "insects", "dirty utensils"],
    "staff_behavior": ["rude", "unprofessional", "appalling attitude", "disrespectful", "dismissive", "poor behavior", "server was"],
    "ambience": ["noisy", "loud", "uncomfortable seating", "unpleasant atmosphere", "overcrowded", "poor lighting", "poor ventilation", "dirty restaurant"],
    "portion_size": ["too small", "still hungry", "pathetically small", "tiny portion", "skimpy portion", "small portion", "poor quantity"],
}



def get_feedback_base_query(db: Session):
    """Reusable base query helper for Feedback model."""
    return db.query(Feedback)


def get_overview_metrics(db: Session, filters: FilterParams) -> Dict[str, Any]:
    """Calculates overview KPI metrics (totals, averages, complaint rate) in a single query."""
    base_query = get_feedback_base_query(db)
    filtered_query, _ = apply_filters(base_query, filters, set())

    stats = filtered_query.with_entities(
        func.count(Feedback.id).label("total_reviews"),
        func.avg(Feedback.rating).label("avg_rating"),
        func.avg(Feedback.wait_time_mins).label("avg_wait_time"),
        func.sum(case((Feedback.rating >= 4, 1), else_=0)).label("positive_review_count"),
        func.sum(case((Feedback.rating == 3, 1), else_=0)).label("neutral_review_count"),
        func.sum(case((Feedback.rating <= 2, 1), else_=0)).label("negative_review_count")
    ).first()

    total = stats.total_reviews or 0
    pos = int(stats.positive_review_count or 0)
    neu = int(stats.neutral_review_count or 0)
    neg = int(stats.negative_review_count or 0)

    avg_rating = round(float(stats.avg_rating), 2) if stats.avg_rating is not None else None
    avg_wait = round(float(stats.avg_wait_time), 2) if stats.avg_wait_time is not None else None
    complaint_rate = round(neg / total, 4) if total > 0 else 0.0

    return {
        "total_reviews": total,
        "avg_rating": avg_rating,
        "avg_wait_time": avg_wait,
        "positive_review_count": pos,
        "neutral_review_count": neu,
        "negative_review_count": neg,
        "complaint_rate": complaint_rate,
    }


def get_rating_trend(db: Session, filters: FilterParams, interval: str) -> List[Dict[str, Any]]:
    """Aggregates rating trend over daily, weekly, or monthly time series."""
    db_interval_map = {
        "daily": "day",
        "weekly": "week",
        "monthly": "month"
    }
    db_interval = db_interval_map.get(interval, "day")

    base_query = get_feedback_base_query(db)
    filtered_query, _ = apply_filters(base_query, filters, set())

    # Truncate and cast date to standard format
    trunc_field = cast(func.date_trunc(db_interval, Feedback.feedback_date), Date)

    trend_query = filtered_query.with_entities(
        trunc_field.label("time_bucket"),
        func.avg(Feedback.rating).label("avg_rating")
    ).group_by(trunc_field).order_by(trunc_field)

    results = trend_query.all()

    return [
        {
            "time_bucket": str(r.time_bucket),
            "avg_rating": round(float(r.avg_rating), 2) if r.avg_rating is not None else None
        }
        for r in results
    ]


def get_branch_performance(db: Session, filters: FilterParams) -> List[Dict[str, Any]]:
    """Aggregates performance by branch, sorting by rating descending (nulls last)."""
    base_query = get_feedback_base_query(db)
    
    # Pre-join necessary tables for the performance report
    query = base_query.join(Branch, Branch.id == Feedback.branch_id)\
                      .join(Brand, Brand.id == Branch.brand_id)\
                      .join(City, City.id == Branch.city_id)

    filtered_query, _ = apply_filters(query, filters, {Branch, Brand, City})

    perf_query = filtered_query.with_entities(
        Branch.name.label("branch_name"),
        Brand.name.label("brand_name"),
        City.name.label("city"),
        func.avg(Feedback.rating).label("avg_rating"),
        func.count(Feedback.id).label("review_count"),
        func.avg(Feedback.wait_time_mins).label("avg_wait_time")
    ).group_by(Branch.id, Brand.id, City.id).order_by(func.avg(Feedback.rating).desc().nullslast())

    results = perf_query.all()

    return [
        {
            "branch_name": r.branch_name,
            "brand_name": r.brand_name,
            "city": r.city,
            "avg_rating": round(float(r.avg_rating), 2) if r.avg_rating is not None else None,
            "review_count": r.review_count,
            "avg_wait_time": round(float(r.avg_wait_time), 2) if r.avg_wait_time is not None else None
        }
        for r in results
    ]


def get_complaints_heuristics(db: Session, filters: FilterParams) -> Dict[str, int]:
    """Scans and returns counts for complaint categories using database keyword OR matching."""
    base_query = get_feedback_base_query(db)
    filtered_query, _ = apply_filters(base_query, filters, set())

    # Build SQL CASE expressions using OR matching across all keywords per category
    select_entities = []
    for category, keywords in COMPLAINT_KEYWORDS.items():
        or_conditions = [Feedback.review_text.ilike(f"%{kw}%") for kw in keywords]
        select_entities.append(
            func.sum(case((or_(*or_conditions), 1), else_=0)).label(category)
        )

    stats = filtered_query.with_entities(*select_entities).first()

    return {
        category: int(getattr(stats, category) or 0)
        for category in COMPLAINT_KEYWORDS.keys()
    }


def get_distributions(db: Session, filters: FilterParams) -> Dict[str, Any]:
    """Retrieves ratings histogram, service types, and cuisines count distributions."""
    base_query = get_feedback_base_query(db)
    filtered_query, _ = apply_filters(base_query, filters, set())

    # 1. Rating Histogram (ratings 1 to 5)
    rating_results = filtered_query.with_entities(
        Feedback.rating,
        func.count(Feedback.id)
    ).group_by(Feedback.rating).all()

    rating_histogram = {r: 0 for r in [1, 2, 3, 4, 5]}
    for rating, count in rating_results:
        rating_histogram[rating] = count

    # 2. Service Type Distribution
    service_results = filtered_query.with_entities(
        Feedback.service_type,
        func.count(Feedback.id)
    ).group_by(Feedback.service_type).all()

    service_dist = {"delivery": 0, "dine-in": 0, "takeaway": 0}
    for s_type, count in service_results:
        if s_type in service_dist:
            service_dist[s_type] = count

    # 3. Cuisine Distribution
    cuisine_results = filtered_query.with_entities(
        Feedback.ordered_cuisine,
        func.count(Feedback.id)
    ).group_by(Feedback.ordered_cuisine).all()

    cuisine_dist = {}
    for cuisine, count in cuisine_results:
        if cuisine:
            cuisine_dist[cuisine] = count

    return {
        "rating_histogram": rating_histogram,
        "service_type_distribution": service_dist,
        "cuisine_distribution": cuisine_dist
    }
