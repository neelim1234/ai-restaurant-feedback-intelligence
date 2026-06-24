"""
backend/services/ai.py - Service layer for compiling SQL context and calling Gemini.
"""

from sqlalchemy.orm import Session
from utils.filters import FilterParams
import services.analytics as analytics_service
from ai.gemini_client import call_gemini
from ai import prompts
import json
import logging

logger = logging.getLogger("uvicorn")

def get_filter_context_label(db: Session, filters: FilterParams) -> str:
    """Generates a human-readable label explaining the active filters."""
    parts = []
    
    if filters.city_id:
        from models.lookup import City
        city = db.query(City).filter(City.id == filters.city_id).first()
        if city:
            parts.append(f"City: {city.name}")
            
    if filters.brand_id:
        from models.org import Brand
        brand = db.query(Brand).filter(Brand.id == filters.brand_id).first()
        if brand:
            parts.append(f"Brand: {brand.name}")
            
    if filters.branch_id:
        from models.org import Branch
        branch = db.query(Branch).filter(Branch.id == filters.branch_id).first()
        if branch:
            parts.append(f"Branch: {branch.name}")
            
    if filters.ordered_cuisine:
        parts.append(f"Cuisine: {filters.ordered_cuisine}")
        
    if filters.service_type:
        parts.append(f"Service Channel: {filters.service_type}")
        
    if filters.price_segment:
        parts.append(f"Price Segment: {filters.price_segment}")
        
    if filters.min_rating or filters.max_rating:
        parts.append(f"Ratings: {filters.min_rating or 1}-{filters.max_rating or 5} Stars")

    return ", ".join(parts) if parts else "Global Baseline"


def get_executive_insights(db: Session, filters: FilterParams) -> dict:
    """
    1. Fetches raw data using existing analytics services.
    2. Compresses it into a compact context.
    3. Prompts Gemini REST API.
    4. Parses and returns structured JSON output.
    """
    # 1. Gather raw data
    overview = analytics_service.get_overview_metrics(db, filters)
    complaints = analytics_service.get_complaints_heuristics(db, filters)
    branch_performance = analytics_service.get_branch_performance(db, filters)
    rating_trend = analytics_service.get_rating_trend(db, filters, interval="weekly")

    # 2. Compress Context
    total = int(overview.get("total_reviews") or 0)
    sentiment_pos_pct = 0.0
    sentiment_neutral_pct = 0.0
    sentiment_negative_pct = 0.0
    if total > 0:
        sentiment_pos_pct = float(overview.get("positive_review_count", 0)) / total * 100
        sentiment_neutral_pct = float(overview.get("neutral_review_count", 0)) / total * 100
        sentiment_negative_pct = float(overview.get("negative_review_count", 0)) / total * 100


    sorted_complaints = sorted(
        complaints.items(),
        key=lambda item: item[1] or 0,
        reverse=True
    )
    top_3_complaints = [
        {"category": cat, "count": int(val or 0)}
        for cat, val in sorted_complaints[:3]
    ]

    worst_3_branches = []
    if branch_performance:
        sorted_worst = sorted(
            branch_performance,
            key=lambda x: x.get("avg_rating") if x.get("avg_rating") is not None else 6.0
        )
        for b in sorted_worst[:3]:
            worst_3_branches.append({
                "branch_name": b.get("branch_name"),
                "brand_name": b.get("brand_name"),
                "city": b.get("city"),
                "avg_rating": float(b.get("avg_rating") or 0.0)
            })

    trend_direction = "stable"
    if len(rating_trend) >= 2:
        midpoint = len(rating_trend) // 2
        first_half = rating_trend[:midpoint]
        second_half = rating_trend[midpoint:]
        
        avg_first = sum(float(pt.get("avg_rating") or 0.0) for pt in first_half) / len(first_half)
        avg_second = sum(float(pt.get("avg_rating") or 0.0) for pt in second_half) / len(second_half)
        
        diff = avg_second - avg_first
        if diff > 0.15:
            trend_direction = "improving"
        elif diff < -0.15:
            trend_direction = "declining"
        else:
            trend_direction = "stable"

    label = get_filter_context_label(db, filters)

    # Explicitly cast numeric values before prompt formatting
    avg_rating_val = float(overview.get("avg_rating") or 0.0)
    avg_wait_time_val = float(overview.get("avg_wait_time") or 0.0)

    # 3. Format Prompt
    prompt = prompts.EXECUTIVE_INSIGHTS_PROMPT.format(
        label=label,
        total_reviews=total,
        avg_rating=avg_rating_val,
        avg_wait_time=avg_wait_time_val,
        sentiment_positive_pct=sentiment_pos_pct,
        sentiment_neutral_pct=sentiment_neutral_pct,
        sentiment_negative_pct=sentiment_negative_pct,
        top_complaints=json.dumps(top_3_complaints),
        worst_branches=json.dumps(worst_3_branches),
        trend_direction=trend_direction
    )

    # 4. Call Gemini and parse result (letting exceptions bubble up)
    response_text = call_gemini(prompt)
    result = json.loads(response_text)
    required_keys = ["summary", "priority_level", "root_causes", "recommendations"]
    for key in required_keys:
        if key not in result:
            raise KeyError(f"Missing required key '{key}' in AI response")
    return result


def get_review_response(review_text: str, rating: int) -> dict:
    """
    Selects prompt adaptive to rating and requests draft response from Gemini.
    """
    if rating <= 2:
        prompt_template = prompts.REVIEW_RESPONSE_APOLOGY_PROMPT
    elif rating >= 4:
        prompt_template = prompts.REVIEW_RESPONSE_GRATITUDE_PROMPT
    else:
        prompt_template = prompts.REVIEW_RESPONSE_NEUTRAL_PROMPT

    prompt = prompt_template.format(
        rating=int(rating),
        review_text=review_text
    )

    # Call Gemini and parse result (letting exceptions bubble up)
    response_text = call_gemini(prompt)
    result = json.loads(response_text)
    if "response" not in result:
        raise KeyError("Missing 'response' key in AI response draft")
    return result
