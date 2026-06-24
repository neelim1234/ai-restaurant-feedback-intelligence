"""
dataset/seed.py - Seeds the database with lookup tables and organization hierarchy.

Run this BEFORE running generator.py in --mode db.

Usage:
    python seed.py              # Full seed (lookups + hierarchy)
    python seed.py --dry-run    # Print what would be inserted without committing

The seed is idempotent: safe to run multiple times. Existing rows are skipped.

Seeded in order:
  1. Lookup tables: cities, cuisines, complaint_categories
  2. Organization: SpiceHub Foods Pvt Ltd
  3. Brands: Urban Tandoor, Thai Bowl, La Cucina, QuickBite
  4. Branches (~17) distributed across cities
  5. BranchCuisine mappings
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as a standalone script
_BACKEND_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(_BACKEND_DIR))

from sqlalchemy.orm import Session

from database import SessionLocal
from models.lookup import City, Cuisine, ComplaintCategory
from models.org import Organization, Brand, Branch, BranchCuisine

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

CITIES = ["Mumbai", "Bangalore", "Pune", "Delhi", "Hyderabad"]

CUISINES = ["Indian", "Thai", "Italian", "Chinese", "Fast Food"]

COMPLAINT_CATEGORIES = [
    "delivery_delay",
    "food_quality",
    "pricing",
    "packaging",
    "hygiene",
    "staff_behavior",
    "ambience",
    "portion_size",
]

ORG_NAME = "SpiceHub Foods Pvt Ltd"

BRANDS = ["Urban Tandoor", "Thai Bowl", "La Cucina", "QuickBite"]

# (brand_name, branch_name, city_name, cuisines_offered)
# ORDER MATTERS — sequential IDs in patterns.py assume this exact order.
BRANCH_DEFINITIONS: list[tuple[str, str, str, list[str]]] = [
    # --- Urban Tandoor ---
    ("Urban Tandoor", "Bandra Branch",           "Mumbai",    ["Indian"]),
    ("Urban Tandoor", "FC Road Branch",           "Pune",      ["Indian"]),
    ("Urban Tandoor", "Connaught Place Branch",   "Delhi",     ["Indian"]),
    ("Urban Tandoor", "Banjara Hills Branch",     "Hyderabad", ["Indian"]),
    # --- Thai Bowl ---
    ("Thai Bowl",    "Andheri Branch",            "Mumbai",    ["Thai", "Chinese"]),
    ("Thai Bowl",    "Kothrud Branch",            "Pune",      ["Thai", "Chinese"]),
    ("Thai Bowl",    "Indiranagar Branch",        "Bangalore", ["Thai", "Chinese"]),
    ("Thai Bowl",    "Lajpat Nagar Branch",       "Delhi",     ["Thai", "Chinese"]),
    # --- La Cucina ---
    ("La Cucina",   "Koramangala Branch",         "Bangalore", ["Italian"]),
    ("La Cucina",   "Juhu Branch",                "Mumbai",    ["Italian"]),
    ("La Cucina",   "Aundh Branch",               "Pune",      ["Italian"]),
    ("La Cucina",   "Hauz Khas Branch",           "Delhi",     ["Italian"]),
    # --- QuickBite ---
    ("QuickBite",   "Dadar Branch",               "Mumbai",    ["Chinese", "Fast Food"]),
    ("QuickBite",   "Whitefield Branch",          "Bangalore", ["Chinese", "Fast Food"]),
    ("QuickBite",   "Saket Branch",               "Delhi",     ["Chinese", "Fast Food"]),
    ("QuickBite",   "HITEC City Branch",          "Hyderabad", ["Chinese", "Fast Food"]),
    ("QuickBite",   "Hinjewadi Branch",           "Pune",      ["Chinese", "Fast Food"]),
]


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

def seed_lookups(db: Session, dry_run: bool = False) -> dict[str, dict]:
    """
    Seeds cities, cuisines, and complaint_categories.
    Returns lookup maps: {name: model_instance} for each table.
    """
    print("\n[Step 1/3] Seeding lookup tables...")

    # Cities
    existing_cities = {c.name: c for c in db.query(City).all()}
    new_cities = 0
    for name in CITIES:
        if name not in existing_cities:
            city = City(name=name)
            if not dry_run:
                db.add(city)
            else:
                city.id = -1  # placeholder for dry run
            existing_cities[name] = city
            new_cities += 1

    if not dry_run:
        db.flush()

    print(f"  Cities:      {len(CITIES)} total, {new_cities} new")

    # Cuisines
    existing_cuisines = {c.name: c for c in db.query(Cuisine).all()}
    new_cuisines = 0
    for name in CUISINES:
        if name not in existing_cuisines:
            cuisine = Cuisine(name=name)
            if not dry_run:
                db.add(cuisine)
            existing_cuisines[name] = cuisine
            new_cuisines += 1

    if not dry_run:
        db.flush()

    print(f"  Cuisines:    {len(CUISINES)} total, {new_cuisines} new")

    # Complaint Categories
    existing_cats = {c.name: c for c in db.query(ComplaintCategory).all()}
    new_cats = 0
    for name in COMPLAINT_CATEGORIES:
        if name not in existing_cats:
            cat = ComplaintCategory(name=name)
            if not dry_run:
                db.add(cat)
            existing_cats[name] = cat
            new_cats += 1

    if not dry_run:
        db.flush()

    print(f"  Complaint categories: {len(COMPLAINT_CATEGORIES)} total, {new_cats} new")

    return {
        "cities":    existing_cities,
        "cuisines":  existing_cuisines,
        "complaint_categories": existing_cats,
    }


def seed_hierarchy(
    db: Session,
    lookups: dict[str, dict],
    dry_run: bool = False,
) -> None:
    """
    Seeds the organization, brands, branches, and branch_cuisines.
    Uses lookups dict returned by seed_lookups().
    """
    print("\n[Step 2/3] Seeding organization hierarchy...")

    city_map    = lookups["cities"]
    cuisine_map = lookups["cuisines"]

    # Organization
    org = db.query(Organization).filter_by(name=ORG_NAME).first()
    if not org:
        org = Organization(name=ORG_NAME)
        if not dry_run:
            db.add(org)
            db.flush()
            db.refresh(org)
        print(f"  Created organization: {ORG_NAME}")
    else:
        print(f"  Organization already exists: {ORG_NAME} (id={org.id})")

    # Brands
    brand_map: dict[str, Brand] = {}
    for brand_name in BRANDS:
        brand = db.query(Brand).filter_by(name=brand_name).first()
        if not brand:
            brand = Brand(org_id=org.id if not dry_run else -1, name=brand_name)
            if not dry_run:
                db.add(brand)
                db.flush()
                db.refresh(brand)
            print(f"  Created brand: {brand_name}")
        brand_map[brand_name] = brand

    # Branches + BranchCuisines
    print("\n[Step 3/3] Seeding branches...")
    new_branches = 0
    for branch_name_key, (brand_name, branch_name, city_name, cuisines_offered) in enumerate(BRANCH_DEFINITIONS, start=1):
        brand  = brand_map[brand_name]
        city   = city_map[city_name]

        branch = db.query(Branch).filter_by(
            brand_id=brand.id, name=branch_name
        ).first() if not dry_run else None

        if not branch:
            branch = Branch(
                brand_id=brand.id if not dry_run else -1,
                name=branch_name,
                city_id=city.id if not dry_run else -1,
            )
            if not dry_run:
                db.add(branch)
                db.flush()
                db.refresh(branch)
            new_branches += 1
            if dry_run:
                print(f"  [DRY RUN] Would create: {brand_name} / {branch_name} ({city_name})")

        # Branch cuisines
        if not dry_run:
            existing_cuisine_ids = {bc.cuisine_id for bc in branch.branch_cuisines}
            for cuisine_name in cuisines_offered:
                cuisine = cuisine_map[cuisine_name]
                if cuisine.id not in existing_cuisine_ids:
                    db.add(BranchCuisine(branch_id=branch.id, cuisine_id=cuisine.id))
        else:
            print(f"  [DRY RUN] Would map cuisines {cuisines_offered} → {branch_name}")

    if not dry_run:
        db.commit()

    print(f"\n  Branches: {len(BRANCH_DEFINITIONS)} total, {new_branches} new")


def print_summary(db: Session) -> None:
    """Print a summary of what was seeded."""
    print("\n" + "=" * 50)
    print("SEED SUMMARY")
    print("=" * 50)
    print(f"  Organizations:        {db.query(Organization).count()}")
    print(f"  Brands:               {db.query(Brand).count()}")
    print(f"  Branches:             {db.query(Branch).count()}")
    print(f"  Branch-Cuisine links: {db.query(BranchCuisine).count()}")
    print(f"  Cities:               {db.query(City).count()}")
    print(f"  Cuisines:             {db.query(Cuisine).count()}")
    print(f"  Complaint categories: {db.query(ComplaintCategory).count()}")

    print("\nBranches seeded (id | brand | name | city):")
    branches = (
        db.query(Branch)
        .join(Brand)
        .join(City)
        .order_by(Branch.id)
        .all()
    )
    for b in branches:
        print(f"  {b.id:3d} | {b.brand.name:<15} | {b.name:<28} | {b.city.name}")
    print("=" * 50)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed the database with lookup tables and organization hierarchy.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be inserted without committing to the database.",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN mode — no changes will be committed.\n")

    db = SessionLocal()
    try:
        lookups = seed_lookups(db, dry_run=args.dry_run)
        seed_hierarchy(db, lookups, dry_run=args.dry_run)

        if not args.dry_run:
            print_summary(db)
            print("\nSeed completed successfully!")
            print("\nNext step:")
            print("  python generator.py --mode db --rows 8500")
        else:
            print("\nDry run complete. No data was written.")

    except Exception as e:
        db.rollback()
        print(f"\nERROR during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
