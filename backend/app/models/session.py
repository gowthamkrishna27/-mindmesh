"""SQLAlchemy 2.x models for MindMesh student assessment sessions and interactions.

Models:
- Student
- Session
- SessionQuestionIssue
- InteractionEvent
- SelectionLog
- DiagnosisSnapshot

Conforms to Specification v3.0 Sections 6, 8, 11, 12, 13.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Student(Base):
    """Student profile and assessment consent status."""

    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Student")
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    consent_given: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consent_given_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    class_id: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    section_id: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("sections.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="student", cascade="all, delete-orphan")


class Session(Base):
    """Assessment session entity (diagnostic, retest, or practice)."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    student_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # diagnostic, retest, practice
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")  # active, completed, abandoned
    question_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=12)
    answered_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    concept_id: Mapped[Optional[str]] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="SET NULL"),
        nullable=True,
    )
    consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    completion_reason: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="sessions")
    question_issues: Mapped[List["SessionQuestionIssue"]] = relationship(
        "SessionQuestionIssue",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    events: Mapped[List["InteractionEvent"]] = relationship(
        "InteractionEvent",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    selection_logs: Mapped[List["SelectionLog"]] = relationship(
        "SelectionLog",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class SessionQuestionIssue(Base):
    """Audit record of a question issued to a student in a session."""

    __tablename__ = "session_question_issues"
    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_session_question_issue"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="issued")  # issued, answered

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="question_issues")


class InteractionEvent(Base):
    """Fine-grained interaction event during question display and answering."""

    __tablename__ = "interaction_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )  # question_displayed, first_interaction, option_changed, hint_requested, submit_intent
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    server_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    client_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="events")


class SelectionLog(Base):
    """Audit log of adaptive question selection decisions and ranking scores."""

    __tablename__ = "selection_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    candidate_scores: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    reason: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="selection_logs")


class DiagnosisSnapshot(Base):
    """Immutable diagnosis snapshot per concept at session submission/completion."""

    __tablename__ = "diagnosis_snapshots"
    __table_args__ = (
        UniqueConstraint("session_id", "concept_id", name="uq_session_concept_snapshot"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    concept_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    epoch_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mastery_estimate: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    direct_estimate: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="unassessed")
    ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    likely_cause: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    also_observed: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    recommended_action: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    suggested_depth: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class LearningCompletion(Base):
    """Record of completed learning resource/concept by a student (Section 6.2, 11.11)."""

    __tablename__ = "learning_completions"
    __table_args__ = (
        UniqueConstraint("student_id", "concept_id", name="uq_student_concept_completion"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    concept_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

