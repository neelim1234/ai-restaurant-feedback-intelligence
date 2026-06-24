"""
models/org.py - Multi-tenant business hierarchy.

Hierarchy: Organization → Brand → Branch
           Branch ←→ Cuisine  (many-to-many via BranchCuisine)

Design notes:
  - V1 uses a single Organization row, but the schema is multi-tenant ready.
  - A Brand belongs to one Organization. Branches belong to one Brand.
  - branch_cuisines represents what cuisines a branch OFFERS (not what
    a customer ordered — that lives in feedbacks.ordered_cuisine).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    brands: Mapped[list["Brand"]] = relationship("Brand", back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name!r}>"


class Brand(Base):
    __tablename__ = "brands"
    __table_args__ = (
        UniqueConstraint("org_id", "name", name="uq_brands_org_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="brands"
    )
    branches: Mapped[list["Branch"]] = relationship("Branch", back_populates="brand")

    def __repr__(self) -> str:
        return f"<Brand id={self.id} name={self.name!r}>"


class Branch(Base):
    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("brand_id", "name", name="uq_branches_brand_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id"), nullable=False, index=True
    )
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    brand: Mapped["Brand"] = relationship("Brand", back_populates="branches")
    city: Mapped["City"] = relationship("City", back_populates="branches")  # type: ignore[name-defined]
    branch_cuisines: Mapped[list["BranchCuisine"]] = relationship(
        "BranchCuisine", back_populates="branch", cascade="all, delete-orphan"
    )
    feedbacks: Mapped[list["Feedback"]] = relationship(  # type: ignore[name-defined]
        "Feedback", back_populates="branch"
    )

    def __repr__(self) -> str:
        return f"<Branch id={self.id} name={self.name!r}>"


class BranchCuisine(Base):
    """
    Junction table: Branch ←→ Cuisine (many-to-many).
    Semantics: cuisines this branch is CAPABLE of serving.
    Distinct from feedbacks.ordered_cuisine (what a customer actually ordered).
    """

    __tablename__ = "branch_cuisines"

    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id"), primary_key=True
    )
    cuisine_id: Mapped[int] = mapped_column(
        ForeignKey("cuisines.id"), primary_key=True
    )

    branch: Mapped["Branch"] = relationship("Branch", back_populates="branch_cuisines")
    cuisine: Mapped["Cuisine"] = relationship(  # type: ignore[name-defined]
        "Cuisine", back_populates="branch_cuisines"
    )

    def __repr__(self) -> str:
        return (
            f"<BranchCuisine branch_id={self.branch_id} cuisine_id={self.cuisine_id}>"
        )
