"""
backend/routers/ai.py - Router configuration for all Gemini AI endpoints.
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import time

from database import get_db
from utils.filters import FilterParams
from schemas.ai import (
    AIInsightsRequest,
    AIResponseRequest
)
import services.ai as ai_service

router = APIRouter(prefix="/api/ai", tags=["AI Integration"])

# In-memory tracking for rate-limiting per client IP
last_request_times = {}

def rate_limiter(request: Request):
    """
    Ensures a minimum spacing of 5 seconds between AI requests per client.
    Cleans up stale memory entries on each request.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()

    # Clean up stale IP records to prevent memory leak (60-second threshold)
    stale_ips = [ip for ip, last_time in last_request_times.items() if now - last_time > 60.0]
    for ip in stale_ips:
        del last_request_times[ip]

    # Validate rate limit (5-second cooldown)
    if client_ip in last_request_times:
        elapsed = now - last_request_times[client_ip]
        if elapsed < 5.0:
            retry_after = round(5.0 - elapsed, 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please retry in {retry_after} seconds."
            )

    last_request_times[client_ip] = now


@router.post("/insights")
def post_ai_insights(
    payload: AIInsightsRequest,
    db: Session = Depends(get_db),
    _ = Depends(rate_limiter)
):
    """Generates structured executive insights from compressed filter metrics context."""
    try:
        filters = FilterParams(
            city_id=payload.city_id,
            branch_id=payload.branch_id,
            brand_id=payload.brand_id,
            ordered_cuisine=payload.ordered_cuisine,
            service_type=payload.service_type,
            price_segment=payload.price_segment,
            min_rating=payload.min_rating,
            max_rating=payload.max_rating,
            start_date=payload.start_date,
            end_date=payload.end_date
        )
        return ai_service.get_executive_insights(db, filters)
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"error": "AI service temporarily unavailable"}
        )


@router.post("/respond")
def post_ai_response(
    payload: AIResponseRequest,
    _ = Depends(rate_limiter)
):
    """Drafts an empathetic, brand-safe response for a single review."""
    try:
        return ai_service.get_review_response(payload.review_text, payload.rating)
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"error": "AI service temporarily unavailable"}
        )
