"""SQLAlchemy 2.x models for MindMesh deterministic engine persistence.

Models:
- Response
- ResponseEvidence
- ConceptEpoch
- StudentConceptMastery

Conforms to Specification v3.0 Sections 7, 12, 13.
"""

from datetime import datetime, timezone
from typing import Any, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Response(Base):
    """Submitted answer response with server-derived interaction signals and reason tags."""

    __tablename__ = "responses"
    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_session_question_response"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_option_key: Mapped[str] = mapped_column(String(8), nullable=False)
    confidence: Mapped[str] = mapped_column(String(32), nullable=False)  # not_sure, fairly_sure, sure
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    assisted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Server-derived timing and signals (Section 7.1)
    client_response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    time_class: Mapped[str] = mapped_column(String(16), nullable=False)  # fast, normal, slow, away
    option_changes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    first_selected_option_id: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    switched_from_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    signals_incomplete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Per-answer reason tags (Section 7.6)
    reason_tags: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    evidence_rows: Mapped[List["ResponseEvidence"]] = relationship(
        "ResponseEvidence",
        back_populates="response",
        cascade="all, delete-orphan",
    )


class ResponseEvidence(Base):
    """Direct or indirect evidence row produced by an answered question."""

    __tablename__ = "response_evidence"
    __table_args__ = (
        UniqueConstraint("response_id", "concept_id", "evidence_type", name="uq_response_concept_evidence_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    response_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("responses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    concept_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    evidence_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )  # primary_direct, mapped_misconception, indirect_prerequisite
    direction: Mapped[str] = mapped_column(String(16), nullable=False)  # positive, negative
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    epoch_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Audit links for indirect / mapped evidence
    source_concept_id: Mapped[Optional[str]] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="SET NULL"),
        nullable=True,
    )
    edge_prerequisite_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    edge_dependent_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationship
    response: Mapped["Response"] = relationship("Response", back_populates="evidence_rows")


class ConceptEpoch(Base):
    """Evidence epoch marker for a student on a specific concept."""

    __tablename__ = "concept_epochs"
    __table_args__ = (
        UniqueConstraint("student_id", "concept_id", "epoch_index", name="uq_student_concept_epoch"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    concept_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    epoch_index: Mapped[int] = mapped_column(Integer, nullable=False)
    opened_by_response_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("responses.id", ondelete="SET NULL"),
        nullable=True,
    )
    opened_by_session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class StudentConceptMastery(Base):
    """Current epoch mastery state, estimates, and counts for a student on a concept."""

    __tablename__ = "student_concept_mastery"
    __table_args__ = (
        UniqueConstraint("student_id", "concept_id", name="uq_student_concept_mastery"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    concept_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    epoch_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Blended evidence totals (includes indirect prerequisite evidence)
    weighted_correct: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    weighted_incorrect: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    mastery_estimate: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Direct evidence totals (direct primary + mapped misconception only)
    direct_weighted_correct: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    direct_weighted_incorrect: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    direct_estimate: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Distinct question counts in current epoch
    n_direct_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_direct_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_direct_incorrect: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_direct_unassisted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_direct_correct_unassisted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_direct_primary: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_direct_mapped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_indirect: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Current epoch status and readiness flag
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="unassessed")
    ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
