"""
dataset/generator.py - Synthetic feedback data generator.

Supports two modes:
  --mode csv   Generate a CSV file (no DB connection needed).
  --mode db    Insert rows directly into PostgreSQL.

Usage:
  python generator.py --mode csv --rows 8500 --output feedback_data.csv
  python generator.py --mode db  --rows 8500

Design:
  - All randomness is driven by weighted distributions defined in patterns.py.
  - Hidden patterns (P1–P10) are applied via named config resolution functions.
  - Review texts are template-based with keyword alignment to the rule-based
    classifier (built in Phase 2), so the classifier can achieve high accuracy.
  - P5 (rating ≤ 2 AND wait_time > 45 correlated) is enforced directly in
    generate_row() by selecting the 'negative_delivery' wait config for low
    ratings on delivery orders.
  - P6 (premium segment → low complaint frequency) is handled by bumping the
    rating upward probabilistically when price_segment='premium'.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import os
import random
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path setup: allow running as a standalone script from any directory.
# For --mode db, this also allows importing database / models.
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(_BACKEND_DIR))

from dataset.patterns import (
    BRANCH_DEFINITIONS,
    BRANCHES_BY_CITY,
    CITY_WEIGHTS,
    COMPLAINT_WEIGHTS,
    DATE_CONFIG,
    NEGATIVE_TEMPLATES,
    NEUTRAL_TEMPLATES,
    ORDER_VALUE_RANGES,
    POSITIVE_TEMPLATES,
    PRICE_SEGMENT_WEIGHTS,
    RATING_WEIGHTS,
    SERVICE_TYPE_WEIGHTS,
    WAIT_TIME_CONFIG,
)

# ---------------------------------------------------------------------------
# Pattern resolution helpers
# Each function returns the NAME of the config to use.
# ---------------------------------------------------------------------------

def resolve_service_type_config(city: str, brand: str) -> str:
    """P1, P3, P4, P9 — service type distribution."""
    if city == "Bangalore" and brand == "La Cucina":
        return "bangalore_lacucina"
    if city == "Delhi" and brand == "QuickBite":
        return "delhi_quickbite"
    if city == "Mumbai":
        return "mumbai"
    if city == "Hyderabad":
        return "hyderabad"
    return "default"


def resolve_rating_config(city: str, brand: str, service_type: str) -> str:
    """P1, P2, P3, P4, P9 — base rating distribution before date modifiers."""
    if city == "Mumbai" and service_type == "delivery":
        return "mumbai_delivery"
    if city == "Pune" and brand == "Thai Bowl":
        return "pune_thai_bowl"
    if city == "Bangalore" and brand == "La Cucina" and service_type == "dine-in":
        return "bangalore_lacucina_dinein"
    if city == "Delhi" and brand == "QuickBite":
        return "delhi_quickbite"
    if city == "Hyderabad" and service_type == "dine-in":
        return "hyderabad_dinein"
    return "default"


def resolve_complaint_config(
    city: str, brand: str, service_type: str,
    price_segment: str, ordered_cuisine: str,
) -> str:
    """P1, P2, P4, P6, P9, P10 — complaint category weights for negative reviews.
    Priority order: most-specific pattern first.
    """
    if city == "Mumbai" and service_type == "delivery":
        return "mumbai_delivery"
    if city == "Pune" and brand == "Thai Bowl":
        return "pune_thai_bowl"
    if city == "Delhi" and brand == "QuickBite" and service_type == "delivery":
        return "delhi_quickbite_delivery"
    if city == "Hyderabad" and service_type == "dine-in":
        return "hyderabad_dinein"
    if ordered_cuisine == "Fast Food" and service_type == "delivery":
        return "fastfood_delivery"
    if price_segment == "premium":
        return "premium"
    return "default"


def resolve_wait_time_config(city: str, service_type: str, rating: int) -> str:
    """P1, P5 — wait time distribution."""
    if service_type == "dine-in":
        return "dinein"
    if city == "Mumbai" and service_type == "delivery":
        return "mumbai_delivery"
    # P5: low rating + delivery → high wait time (intentional correlation)
    if service_type in ("delivery", "takeaway") and rating <= 2:
        return "negative_delivery"
    return "default"


# ---------------------------------------------------------------------------
# Generation helpers
# ---------------------------------------------------------------------------

def shift_rating_weights(weights: list[float], delta: float) -> list[float]:
    """
    Nudge rating distribution up (delta > 0) or down (delta < 0).
    Uses a position-weighted scaling: lower ratings boosted for negative delta.
    Weights are renormalized after adjustment.
    """
    adjusted = []
    for i, w in enumerate(weights):
        # position: i=0 (rating 1) → pos=-0.5, i=4 (rating 5) → pos=+0.5
        position = (i / 4.0) - 0.5
        factor = max(0.001, 1.0 + position * delta * 2.0)
        adjusted.append(w * factor)
    total = sum(adjusted)
    return [a / total for a in adjusted]


def get_service_type(city: str, brand: str) -> str:
    config_name = resolve_service_type_config(city, brand)
    weights = SERVICE_TYPE_WEIGHTS[config_name]
    return random.choices(["delivery", "dine-in", "takeaway"], weights=weights)[0]


def get_price_segment(brand: str) -> str:
    cfg = PRICE_SEGMENT_WEIGHTS.get(brand, PRICE_SEGMENT_WEIGHTS["default"])
    segments = list(cfg.keys())
    weights = list(cfg.values())
    return random.choices(segments, weights=weights)[0]


def get_rating(
    city: str, brand: str, service_type: str, feedback_date: datetime.date
) -> int:
    config_name = resolve_rating_config(city, brand, service_type)
    weights = list(RATING_WEIGHTS[config_name])

    # P7: Friday (4) / Saturday (5) → rating dip
    if feedback_date.weekday() in (4, 5):
        weights = shift_rating_weights(weights, -DATE_CONFIG["weekend_rating_dip"])

    # P8: Q4 months → rating uplift (festive season)
    if feedback_date.month in DATE_CONFIG["q4_months"]:
        weights = shift_rating_weights(weights, DATE_CONFIG["q4_rating_uplift"])

    return random.choices([1, 2, 3, 4, 5], weights=weights)[0]


def get_wait_time_mins(city: str, service_type: str, rating: int) -> Optional[int]:
    """Returns wait time in minutes, or None (~8% of rows)."""
    if random.random() < 0.08:
        return None
    config_name = resolve_wait_time_config(city, service_type, rating)
    cfg = WAIT_TIME_CONFIG[config_name]
    raw = random.gauss(cfg["mean"], cfg["std"])
    return int(max(cfg["min"], min(cfg["max"], raw)))


def get_complaint_category(
    city: str, brand: str, service_type: str,
    price_segment: str, ordered_cuisine: str,
) -> str:
    config_name = resolve_complaint_config(city, brand, service_type, price_segment, ordered_cuisine)
    cfg = COMPLAINT_WEIGHTS[config_name]
    categories = list(cfg.keys())
    weights = list(cfg.values())
    return random.choices(categories, weights=weights)[0]


def get_order_value(price_segment: str) -> Optional[float]:
    """Returns order value in INR, or None (~10% of rows)."""
    if random.random() < 0.10:
        return None
    lo, hi = ORDER_VALUE_RANGES.get(price_segment, (200, 600))
    return round(random.uniform(lo, hi), 2)


def get_review_text(
    rating: int,
    complaint: Optional[str],
    wait_time: Optional[int],
    cuisine: str,
    city: str,
) -> str:
    """
    Selects a template based on rating/complaint and fills format placeholders.
    All templates accept {wait}, {cuisine}, {city} — unused ones are ignored.
    """
    wait_val = wait_time if wait_time is not None else random.randint(35, 65)
    fmt = {"wait": wait_val, "cuisine": cuisine, "city": city}

    if rating >= 4:
        template = random.choice(POSITIVE_TEMPLATES)
    elif rating == 3:
        template = random.choice(NEUTRAL_TEMPLATES)
    else:
        # Negative review — use complaint-specific template
        if complaint and complaint in NEGATIVE_TEMPLATES:
            template = random.choice(NEGATIVE_TEMPLATES[complaint])
        else:
            template = random.choice(NEGATIVE_TEMPLATES["food_quality"])

    return template.format_map(_SafeFormatMap(fmt))


class _SafeFormatMap(dict):
    """dict subclass that returns '{key}' unchanged for missing keys."""
    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


# ---------------------------------------------------------------------------
# Date generation — respects P7 (Fri/Sat volume spike)
# ---------------------------------------------------------------------------

def generate_dates(n: int) -> list[datetime.date]:
    """
    Returns n dates sampled (with replacement) from the configured date range.
    Friday and Saturday have 40% higher weight to implement P7.
    """
    start = datetime.date.fromisoformat(DATE_CONFIG["start"])
    end   = datetime.date.fromisoformat(DATE_CONFIG["end"])
    dow_weights = DATE_CONFIG["dow_weights"]

    all_dates: list[datetime.date] = []
    weights: list[float] = []

    current = start
    while current <= end:
        all_dates.append(current)
        weights.append(dow_weights[current.weekday()])
        current += datetime.timedelta(days=1)

    return random.choices(all_dates, weights=weights, k=n)


# ---------------------------------------------------------------------------
# Core row generation
# ---------------------------------------------------------------------------

def generate_row(branch: dict, feedback_date: datetime.date) -> dict:
    """
    Generates a single feedback row applying all applicable patterns.

    Returns a flat dict with all CSV/DB columns plus '_complaint_hint'
    (not stored in DB — useful for validation and debugging patterns).
    """
    city    = branch["city"]
    brand   = branch["brand"]

    service_type    = get_service_type(city, brand)
    price_segment   = get_price_segment(brand)
    ordered_cuisine = random.choice(branch["cuisines"])

    rating = get_rating(city, brand, service_type, feedback_date)

    # P6: Premium segment → low complaint frequency.
    # Probabilistically bump low ratings upward before processing complaints.
    if price_segment == "premium" and rating <= 2 and random.random() < 0.45:
        rating += 2

    wait_time  = get_wait_time_mins(city, service_type, rating)
    order_value = get_order_value(price_segment)

    # Determine complaint for negative / mixed reviews
    complaint: Optional[str] = None
    if rating <= 3:
        complaint = get_complaint_category(city, brand, service_type, price_segment, ordered_cuisine)

    review_text = get_review_text(rating, complaint, wait_time, ordered_cuisine, city)

    return {
        # --- DB columns ---
        "branch_id":       branch["id"],   # expected sequential ID from seed
        "ordered_cuisine": ordered_cuisine,
        "service_type":    service_type,
        "price_segment":   price_segment,
        "rating":          rating,
        "review_text":     review_text,
        "order_value":     order_value,
        "wait_time_mins":  wait_time,
        "feedback_date":   feedback_date.isoformat(),
        # --- Readable metadata (CSV only, not in DB schema) ---
        "branch_name":     branch["name"],
        "brand_name":      brand,
        "city":            city,
        # --- Debug hint (not stored) ---
        "_complaint_hint": complaint,
    }


def generate_all_rows(n: int) -> list[dict]:
    dates    = generate_dates(n)
    branches = [
        random.choice(BRANCHES_BY_CITY[
            random.choices(
                list(CITY_WEIGHTS.keys()),
                weights=list(CITY_WEIGHTS.values()),
            )[0]
        ])
        for _ in range(n)
    ]
    return [generate_row(branch, date) for branch, date in zip(branches, dates)]


# ---------------------------------------------------------------------------
# Output modes
# ---------------------------------------------------------------------------

# Columns written to the DB (must match Feedback table columns exactly)
_DB_COLUMNS = [
    "branch_id", "ordered_cuisine", "service_type", "price_segment",
    "rating", "review_text", "order_value", "wait_time_mins", "feedback_date",
]

# Columns written to CSV (includes readable metadata for demo/import purposes)
_CSV_COLUMNS = [
    "branch_id", "branch_name", "brand_name", "city",
    "ordered_cuisine", "service_type", "price_segment",
    "rating", "review_text", "order_value", "wait_time_mins", "feedback_date",
]


def write_csv(rows: list[dict], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows)} rows to {output_path}")


def write_db(rows: list[dict]) -> None:
    """Bulk-insert feedback rows into PostgreSQL using SQLAlchemy Core for speed."""
    from database import engine
    from models.feedback import Feedback
    from sqlalchemy import insert

    # Verify branches exist
    from database import SessionLocal
    from models.org import Branch as BranchModel

    db = SessionLocal()
    try:
        branch_ids_in_db = {b.id for b in db.query(BranchModel.id).all()}
        expected_ids = {b["id"] for b in BRANCH_DEFINITIONS}
        missing = expected_ids - branch_ids_in_db
        if missing:
            print(
                f"  ERROR: Branch IDs {sorted(missing)} not found in DB.\n"
                f"  Run seed.py first before generating in --mode db."
            )
            sys.exit(1)
    finally:
        db.close()

    # Strip non-DB keys and replace None-string with actual None
    db_rows = []
    for r in rows:
        db_rows.append({col: r[col] for col in _DB_COLUMNS})

    # Bulk insert in batches of 500 for memory efficiency
    batch_size = 500
    total = len(db_rows)
    inserted = 0

    with engine.begin() as conn:
        for i in range(0, total, batch_size):
            batch = db_rows[i : i + batch_size]
            conn.execute(insert(Feedback), batch)
            inserted += len(batch)
            print(f"  Inserted {inserted}/{total} rows...", end="\r")

    print(f"\n  Inserted {total} rows into feedbacks table.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synthetic feedback data generator for the AI Restaurant Feedback Intelligence Platform.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generator.py --mode csv --rows 8500
  python generator.py --mode csv --rows 8500 --output my_data.csv
  python generator.py --mode db  --rows 8500

Note: For --mode db, run seed.py first to populate the branch hierarchy.
      The .env file must be present with a valid DATABASE_URL.
""",
    )
    parser.add_argument(
        "--mode",
        choices=["csv", "db"],
        required=True,
        help="Output mode: 'csv' writes a file, 'db' inserts into PostgreSQL.",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=8500,
        help="Number of feedback rows to generate (default: 8500).",
    )
    parser.add_argument(
        "--output",
        default="feedback_data.csv",
        help="CSV output file path (only used with --mode csv, default: feedback_data.csv).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible output (optional).",
    )

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        print(f"  Random seed set to {args.seed}")

    print(f"\nGenerating {args.rows} rows (mode={args.mode})...")
    rows = generate_all_rows(args.rows)

    if args.mode == "csv":
        write_csv(rows, args.output)
        print(f"\nDone. CSV written to: {args.output}")
    else:
        write_db(rows)
        print("\nDone. Feedbacks inserted into database.")

    # Quick pattern summary
    neg_count = sum(1 for r in rows if r["rating"] <= 2)
    pos_count = sum(1 for r in rows if r["rating"] >= 4)
    print(f"\nDistribution summary:")
    print(f"  Positive (4-5 stars): {pos_count:,}  ({pos_count/len(rows)*100:.1f}%)")
    print(f"  Negative (1-2 stars): {neg_count:,}  ({neg_count/len(rows)*100:.1f}%)")
    print(f"  Neutral  (3 stars):   {len(rows)-pos_count-neg_count:,}  ({(len(rows)-pos_count-neg_count)/len(rows)*100:.1f}%)")


if __name__ == "__main__":
    main()
