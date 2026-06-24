"""
models/lookup.py - Lookup / reference tables.

These are the three normalized lookup tables required by the architecture:
  - City        (analytics pivot, foreign-keyed from branches)
  - Cuisine     (analytics pivot, foreign-keyed from branch_cuisines)
  - ComplaintCategory  (analytics pivot, foreign-keyed from feedback_analysis)

All other categorical fields (service_type, price_segment, sentiment,
ordered_cuisine) are stored as constrained VARCHAR columns — see feedback.py.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Reverse relationship: branches in this city
    branches: Mapped[list["Branch"]] = relationship(  # type: ignore[name-defined]
        "Branch", back_populates="city"
    )

    def __repr__(self) -> str:
        return f"<City id={self.id} name={self.name!r}>"


class Cuisine(Base):
    __tablename__ = "cuisines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Reverse relationship: branches that offer this cuisine
    branch_cuisines: Mapped[list["BranchCuisine"]] = relationship(  # type: ignore[name-defined]
        "BranchCuisine", back_populates="cuisine"
    )

    def __repr__(self) -> str:
        return f"<Cuisine id={self.id} name={self.name!r}>"


class ComplaintCategory(Base):
    __tablename__ = "complaint_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Note: No back_populates to FeedbackAnalysis here.
    # FeedbackAnalysis has TWO FK references to this table (primary + secondary),
    # so we keep relationships unidirectional to avoid ambiguity.

    def __repr__(self) -> str:
        return f"<ComplaintCategory id={self.id} name={self.name!r}>"
