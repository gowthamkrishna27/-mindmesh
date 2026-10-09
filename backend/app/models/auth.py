"""SQLAlchemy 2.x models for Educator and Administrator identity, access, and audit.

Conforms to Specification v3.0 Sections 11.0, 19.1-19.7.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class AdministratorAccount(Base):
    """Administrator account entity.
    
    Created exclusively through one-time secure CLI bootstrap.
    """

    __tablename__ = "administrator_accounts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    approved_educators: Mapped[List["Educator"]] = relationship(
        "Educator", back_populates="approved_by_admin"
    )
    audit_events: Mapped[List["AdminAuditEvent"]] = relationship(
        "AdminAuditEvent", back_populates="actor_admin"
    )


class Educator(Base):
    """Educator identity entity.
    
    Status transitions: pending -> approved / rejected -> suspended.
    """

    __tablename__ = "educators"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    approved_by_admin_id: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("administrator_accounts.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    # Relationships
    approved_by_admin: Mapped[Optional["AdministratorAccount"]] = relationship(
        "AdministratorAccount", back_populates="approved_educators"
    )
    assignments: Mapped[List["EducatorClassAssignment"]] = relationship(
        "EducatorClassAssignment", back_populates="educator", cascade="all, delete-orphan"
    )


class Class(Base):
    """Academic class entity."""

    __tablename__ = "classes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    sections: Mapped[List["Section"]] = relationship(
        "Section", back_populates="owning_class", cascade="all, delete-orphan"
    )
    assignments: Mapped[List["EducatorClassAssignment"]] = relationship(
        "EducatorClassAssignment", back_populates="assigned_class", cascade="all, delete-orphan"
    )


class Section(Base):
    """Academic section belonging to a class."""

    __tablename__ = "sections"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    class_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        UniqueConstraint("class_id", "code", name="uq_section_class_code"),
    )

    # Relationships
    owning_class: Mapped["Class"] = relationship("Class", back_populates="sections")
    assignments: Mapped[List["EducatorClassAssignment"]] = relationship(
        "EducatorClassAssignment", back_populates="assigned_section", cascade="all, delete-orphan"
    )


class EducatorClassAssignment(Base):
    """Assignment linking an educator to a class and optional section."""

    __tablename__ = "educator_class_assignments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    educator_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("educators.id", ondelete="CASCADE"), nullable=False, index=True
    )
    class_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_id: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("sections.id", ondelete="CASCADE"), nullable=True, index=True
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_by_admin_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("administrator_accounts.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    educator: Mapped["Educator"] = relationship("Educator", back_populates="assignments")
    assigned_class: Mapped["Class"] = relationship("Class", back_populates="assignments")
    assigned_section: Mapped[Optional["Section"]] = relationship("Section", back_populates="assignments")


class AdminAuditEvent(Base):
    """Immutable audit log for security-relevant administrator actions."""

    __tablename__ = "admin_audit_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    actor_admin_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("administrator_accounts.id"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    actor_admin: Mapped["AdministratorAccount"] = relationship(
        "AdministratorAccount", back_populates="audit_events"
    )
