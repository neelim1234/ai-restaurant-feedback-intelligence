"""
models/feedback.py - Core fact table and preprocessing results.

Feedback      — one row per customer review.
FeedbackAnalysis — one-to-one with Feedback; stores structured AI/rule output.

Design decisions:
  - ordered_cuisine is a CHECK-constrained VARCHAR on feedbacks (not a FK).
    It represents what the customer actually ordered, distinct from the
    branch_cuisines junction table (what the branch is capable of serving).
  - is_processed is intentionally absent. The existence of a FeedbackAnalysis
    row is the canonical "processed" signal. Unprocessed feedbacks are found
    via: LEFT JOIN feedback_analysis WHERE fa.id IS NULL.
  - classified_by tracks which pipeline path was used (rules vs gemini).
    This enables audit and performance analysis of the classifier.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Feedback(Base):
    __tablename__ = "feedbacks"
    __table_args__ = (
        # --- CHECK constraints ---
        CheckConstraint(
            "ordered_cuisine IN ('Indian', 'Thai', 'Italian', 'Chinese', 'Fast Food')",
            name="ck_feedbacks_ordered_cuisine",
        ),
        CheckConstraint(
            "service_type IN ('delivery', 'dine-in', 'takeaway')",
            name="ck_feedbacks_service_type",
        ),
        CheckConstraint(
            "price_segment IN ('budget', 'mid-range', 'premium')",
            name="ck_feedbacks_price_segment",
        ),
        CheckConstraint(
            "rating BETWEEN 1 AND 5",
            name="ck_feedbacks_rating",
        ),
        CheckConstraint(
            "wait_time_mins IS NULL OR wait_time_mins >= 0",
            name="ck_feedbacks_wait_time",
        ),
        # --- Compound index for time-range analytics on a branch ---
        Index("ix_feedbacks_branch_date", "branch_id", "feedback_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id"), nullable=False
    )

    # Cuisine the customer actually ordered — nullable for legacy/ambiguous records.
    # Distinct from branch_cuisines (what the branch offers).
    ordered_cuisine: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True
    )

    service_type: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )

    price_segment: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    rating: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, index=True
    )

    review_text: Mapped[str] = mapped_column(Text, nullable=False)

    order_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2), nullable=True
    )

    wait_time_mins: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True
    )

    feedback_date: Mapped[date] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # --- Relationships ---
    branch: Mapped["Branch"] = relationship(  # type: ignore[name-defined]
        "Branch", back_populates="feedbacks"
    )
    analysis: Mapped[Optional["FeedbackAnalysis"]] = relationship(
        "FeedbackAnalysis",
        back_populates="feedback",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Feedback id={self.id} rating={self.rating} "
            f"branch_id={self.branch_id} date={self.feedback_date}>"
        )


class FeedbackAnalysis(Base):
    """
    Preprocessing result for a Feedback row.

    Populated by the hybrid classification pipeline (Phase 2):
      - Rule-based classifier runs first (classified_by='rules')
      - Gemini handles ambiguous / low-confidence reviews (classified_by='gemini')

    To find unprocessed feedbacks:
        SELECT f.id
        FROM feedbacks f
        LEFT JOIN feedback_analysis fa ON fa.feedback_id = f.id
        WHERE fa.id IS NULL;
    """

    __tablename__ = "feedback_analysis"
    __table_args__ = (
        CheckConstraint(
            "sentiment IN ('positive', 'neutral', 'negative')",
            name="ck_analysis_sentiment",
        ),
        CheckConstraint(
            "severity_score BETWEEN 1 AND 5",
            name="ck_analysis_severity_score",
        ),
        CheckConstraint(
            "classified_by IN ('rules', 'gemini')",
            name="ck_analysis_classified_by",
        ),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_analysis_confidence_score",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    feedback_id: Mapped[int] = mapped_column(
        ForeignKey("feedbacks.id"), unique=True, nullable=False
    )

    sentiment: Mapped[str] = mapped_column(String(10), nullable=False)

    severity_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)

    # Two FK references to complaint_categories — kept as separate columns
    # without back_populates on ComplaintCategory to avoid ambiguity.
    primary_complaint_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("complaint_categories.id"), nullable=True
    )
    secondary_complaint_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("complaint_categories.id"), nullable=True
    )

    positive_aspects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    negative_aspects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 'rules' | 'gemini' — critical for classifier performance audit
    classified_by: Mapped[str] = mapped_column(String(10), nullable=False)

    # For rules path: keyword match ratio (0.0–1.0).
    # For gemini path: NULL (Gemini does not self-report confidence here).
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 3), nullable=True
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # --- Relationships ---
    feedback: Mapped["Feedback"] = relationship("Feedback", back_populates="analysis")

    primary_complaint: Mapped[Optional["ComplaintCategory"]] = relationship(  # type: ignore[name-defined]
        "ComplaintCategory",
        foreign_keys=[primary_complaint_id],
    )
    secondary_complaint: Mapped[Optional["ComplaintCategory"]] = relationship(  # type: ignore[name-defined]
        "ComplaintCategory",
        foreign_keys=[secondary_complaint_id],
    )

    def __repr__(self) -> str:
        return (
            f"<FeedbackAnalysis id={self.id} feedback_id={self.feedback_id} "
            f"sentiment={self.sentiment!r} classified_by={self.classified_by!r}>"
        )
