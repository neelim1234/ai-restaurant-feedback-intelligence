"""
models/__init__.py

Imports all models so SQLAlchemy registers them with Base.metadata.
Alembic's autogenerate reads from Base.metadata — every model must be
imported here before any migration is generated or run.
"""

from database import Base  # noqa: F401 — Base must be imported first

from models.lookup import City, Cuisine, ComplaintCategory  # noqa: F401
from models.org import Organization, Brand, Branch, BranchCuisine  # noqa: F401
from models.feedback import Feedback, FeedbackAnalysis  # noqa: F401

__all__ = [
    "Base",
    "City",
    "Cuisine",
    "ComplaintCategory",
    "Organization",
    "Brand",
    "Branch",
    "BranchCuisine",
    "Feedback",
    "FeedbackAnalysis",
]
