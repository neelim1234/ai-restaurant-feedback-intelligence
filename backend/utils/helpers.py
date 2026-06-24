"""
utils/helpers.py - Shared utility functions used across the application.

Phase 1: Basic helpers only.
Phase 2+: Filter builder, pagination, and response formatters will be added here.
"""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any, TypeVar

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

def paginate(query_result: list[T], page: int, page_size: int) -> dict[str, Any]:
    """
    Simple in-memory paginator. For large datasets, pagination should be
    done at the SQL level (LIMIT / OFFSET) in the service layer.

    Args:
        query_result: Full result list.
        page:         1-indexed page number.
        page_size:    Number of items per page.

    Returns:
        {
          "items":       [...],
          "total":       int,
          "page":        int,
          "page_size":   int,
          "total_pages": int,
          "has_next":    bool,
          "has_prev":    bool,
        }
    """
    total = len(query_result)
    total_pages = max(1, math.ceil(total / page_size))
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end   = start + page_size

    return {
        "items":       query_result[start:end],
        "total":       total,
        "page":        page,
        "page_size":   page_size,
        "total_pages": total_pages,
        "has_next":    page < total_pages,
        "has_prev":    page > 1,
    }


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def parse_date(value: str | date | None) -> date | None:
    """Parse an ISO date string to a date object. Returns None for None input."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def date_to_str(value: date | datetime | None, fmt: str = "%Y-%m-%d") -> str | None:
    """Format a date/datetime to string. Returns None for None input."""
    if value is None:
        return None
    return value.strftime(fmt)


def current_utc() -> datetime:
    """Return the current UTC datetime (timezone-naive for simplicity)."""
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Number formatters
# ---------------------------------------------------------------------------

def round_rating(value: float | None, decimals: int = 2) -> float | None:
    """Round a rating value. Returns None for None input."""
    if value is None:
        return None
    return round(float(value), decimals)


def safe_percentage(numerator: int, denominator: int) -> float:
    """Returns percentage (0.0–100.0), or 0.0 if denominator is zero."""
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 1)
