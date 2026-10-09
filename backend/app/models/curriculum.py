"""SQLAlchemy 2.x models for MindMesh curriculum.

Models:
- Concept
- PrerequisiteEdge
- Question
- QuestionOption
- QuestionHint
- Resource

Conforms to Specification v3.0 Sections 4, 5, 12.
"""

from typing import List, Optional
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Concept(Base):
    """Concept node in the dependency graph."""

    __tablename__ = "concepts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    learning_objective: Mapped[str] = mapped_column(Text, nullable=False)
    branch: Mapped[str] = mapped_column(String(64), nullable=False)  # Foundation, Design, SQL
    resource_unavailable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="primary_concept",
        cascade="all, delete-orphan",
    )
    resources: Mapped[List["Resource"]] = relationship(
        "Resource",
        back_populates="concept",
        cascade="all, delete-orphan",
    )
    outgoing_edges: Mapped[List["PrerequisiteEdge"]] = relationship(
        "PrerequisiteEdge",
        foreign_keys="[PrerequisiteEdge.prerequisite_id]",
        back_populates="prerequisite",
        cascade="all, delete-orphan",
    )
    incoming_edges: Mapped[List["PrerequisiteEdge"]] = relationship(
        "PrerequisiteEdge",
        foreign_keys="[PrerequisiteEdge.dependent_id]",
        back_populates="dependent",
        cascade="all, delete-orphan",
    )


class PrerequisiteEdge(Base):
    """Directed edge in the concept dependency graph (prerequisite -> dependent)."""

    __tablename__ = "prerequisite_edges"
    __table_args__ = (
        CheckConstraint("prerequisite_id != dependent_id", name="check_no_self_edge"),
    )

    prerequisite_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    dependent_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        primary_key=True,
    )

    prerequisite: Mapped["Concept"] = relationship(
        "Concept",
        foreign_keys=[prerequisite_id],
        back_populates="outgoing_edges",
    )
    dependent: Mapped["Concept"] = relationship(
        "Concept",
        foreign_keys=[dependent_id],
        back_populates="incoming_edges",
    )


class Question(Base):
    """Curriculum question item."""

    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint("difficulty >= 1 AND difficulty <= 5", name="check_question_difficulty_range"),
        CheckConstraint("expected_time_s > 0", name="check_question_expected_time_positive"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    primary_concept_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    learning_objective_id: Mapped[str] = mapped_column(String(64), nullable=False)
    question_family: Mapped[str] = mapped_column(String(64), nullable=False)  # recognition, interpretation, application, error_analysis
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    expected_time_s: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False, default="reviewed")  # reviewed, draft, needs_review
    use_for_diagnosis: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    use_for_retest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    variant_group: Mapped[str] = mapped_column(String(64), nullable=False)

    # Relationships
    primary_concept: Mapped["Concept"] = relationship("Concept", back_populates="questions")
    options: Mapped[List["QuestionOption"]] = relationship(
        "QuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.option_key",
    )
    hints: Mapped[List["QuestionHint"]] = relationship(
        "QuestionHint",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionHint.hint_level",
    )


class QuestionOption(Base):
    """Option for a multiple-choice question."""

    __tablename__ = "question_options"
    __table_args__ = (
        UniqueConstraint("question_id", "option_key", name="uq_question_option_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    option_key: Mapped[str] = mapped_column(String(8), nullable=False)  # A, B, C, D
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Distractor mapping to misconception / concept
    maps_to_concept_id: Mapped[Optional[str]] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="SET NULL"),
        nullable=True,
    )
    misconception_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    misconception_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    question: Mapped["Question"] = relationship("Question", back_populates="options")
    mapped_concept: Mapped[Optional["Concept"]] = relationship("Concept")


class QuestionHint(Base):
    """Progressive hint for practice sessions."""

    __tablename__ = "question_hints"
    __table_args__ = (
        UniqueConstraint("question_id", "hint_level", name="uq_question_hint_level"),
        CheckConstraint("hint_level IN (1, 2)", name="check_hint_level_1_or_2"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    hint_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 (nudge), 2 (conceptual clue)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    question: Mapped["Question"] = relationship("Question", back_populates="hints")


class Resource(Base):
    """Curated learning resource for a concept across depth levels."""

    __tablename__ = "resources"
    __table_args__ = (
        UniqueConstraint("concept_id", "depth", name="uq_concept_resource_depth"),
        CheckConstraint(
            "depth IN ('quick_revision', 'standard', 'deep_learning')",
            name="check_resource_depth_valid",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    concept_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    depth: Mapped[str] = mapped_column(String(32), nullable=False)  # quick_revision, standard, deep_learning
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    concept: Mapped["Concept"] = relationship("Concept", back_populates="resources")
