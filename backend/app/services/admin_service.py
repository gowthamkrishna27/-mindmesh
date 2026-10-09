"""Administrator workflows service for educator approvals, suspensions, and assignments.

Conforms to Specification v3.0 Sections 19.2, 19.3, 19.6.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.errors import BadRequestError, ConflictError, NotFoundError
from app.models.auth import (
    AdminAuditEvent,
    Class,
    Educator,
    EducatorClassAssignment,
    Section,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def list_educators(
    status_filter: Optional[str],
    db: Session,
) -> List[Educator]:
    """List educator accounts optionally filtered by status."""
    query = db.query(Educator)
    if status_filter:
        query = query.filter(Educator.status == status_filter.strip().lower())
    return query.order_by(Educator.created_at.desc()).all()


def approve_educator(
    admin_id: str,
    educator_id: str,
    db: Session,
) -> Educator:
    """Approve a pending educator application."""
    educator = db.query(Educator).filter(Educator.id == educator_id).first()
    if not educator:
        raise NotFoundError("Educator not found", code="EDUCATOR_NOT_FOUND")

    if educator.status != "pending":
        raise ConflictError(
            f"Cannot approve educator with status '{educator.status}'. Only pending accounts can be approved.",
            code="INVALID_STATE_TRANSITION",
        )

    now = utcnow()
    educator.status = "approved"
    educator.approved_by_admin_id = admin_id
    educator.approved_at = now
    educator.updated_at = now

    audit = AdminAuditEvent(
        actor_admin_id=admin_id,
        action="approve_educator",
        target_type="educator",
        target_id=educator.id,
        metadata_json={"previous_status": "pending", "new_status": "approved"},
    )
    db.add(audit)
    db.commit()
    db.refresh(educator)
    return educator


def reject_educator(
    admin_id: str,
    educator_id: str,
    db: Session,
) -> Educator:
    """Reject a pending educator application."""
    educator = db.query(Educator).filter(Educator.id == educator_id).first()
    if not educator:
        raise NotFoundError("Educator not found", code="EDUCATOR_NOT_FOUND")

    if educator.status != "pending":
        raise ConflictError(
            f"Cannot reject educator with status '{educator.status}'. Only pending accounts can be rejected.",
            code="INVALID_STATE_TRANSITION",
        )

    now = utcnow()
    educator.status = "rejected"
    educator.updated_at = now

    audit = AdminAuditEvent(
        actor_admin_id=admin_id,
        action="reject_educator",
        target_type="educator",
        target_id=educator.id,
        metadata_json={"previous_status": "pending", "new_status": "rejected"},
    )
    db.add(audit)
    db.commit()
    db.refresh(educator)
    return educator


def suspend_educator(
    admin_id: str,
    educator_id: str,
    db: Session,
) -> Educator:
    """Suspend/revoke an educator account. Immediate effect on next request."""
    educator = db.query(Educator).filter(Educator.id == educator_id).first()
    if not educator:
        raise NotFoundError("Educator not found", code="EDUCATOR_NOT_FOUND")

    prev_status = educator.status
    now = utcnow()
    educator.status = "suspended"
    educator.updated_at = now

    audit = AdminAuditEvent(
        actor_admin_id=admin_id,
        action="suspend_educator",
        target_type="educator",
        target_id=educator.id,
        metadata_json={"previous_status": prev_status, "new_status": "suspended"},
    )
    db.add(audit)
    db.commit()
    db.refresh(educator)
    return educator


def create_assignment(
    admin_id: str,
    educator_id: str,
    class_id: str,
    section_id: Optional[str],
    db: Session,
) -> EducatorClassAssignment:
    """Assign an approved educator to a class and optional section."""
    educator = db.query(Educator).filter(Educator.id == educator_id).first()
    if not educator:
        raise NotFoundError("Educator not found", code="EDUCATOR_NOT_FOUND")

    if educator.status != "approved":
        raise BadRequestError(
            f"Cannot assign class to educator with status '{educator.status}'. Educator must be approved.",
            code="EDUCATOR_NOT_APPROVED",
        )

    # Validate class exists
    target_class = db.query(Class).filter(Class.id == class_id).first()
    if not target_class:
        raise NotFoundError("Class not found", code="CLASS_NOT_FOUND")

    # If section_id is specified, validate section exists and belongs to class
    if section_id:
        target_section = db.query(Section).filter(Section.id == section_id).first()
        if not target_section:
            raise NotFoundError("Section not found", code="SECTION_NOT_FOUND")
        if target_section.class_id != class_id:
            raise BadRequestError(
                "Section does not belong to the specified class",
                code="SECTION_CLASS_MISMATCH",
            )

    # Prevent duplicate active assignment
    existing_active = (
        db.query(EducatorClassAssignment)
        .filter(
            EducatorClassAssignment.educator_id == educator_id,
            EducatorClassAssignment.class_id == class_id,
            EducatorClassAssignment.section_id == section_id,
            EducatorClassAssignment.active.is_(True),
        )
        .first()
    )
    if existing_active:
        raise ConflictError(
            "Educator already has an active assignment for this class/section",
            code="DUPLICATE_ASSIGNMENT",
        )

    assignment = EducatorClassAssignment(
        educator_id=educator_id,
        class_id=class_id,
        section_id=section_id,
        active=True,
        created_by_admin_id=admin_id,
    )
    db.add(assignment)
    db.flush()

    audit = AdminAuditEvent(
        actor_admin_id=admin_id,
        action="assign_scope",
        target_type="assignment",
        target_id=assignment.id,
        metadata_json={
            "educator_id": educator_id,
            "class_id": class_id,
            "section_id": section_id,
        },
    )
    db.add(audit)
    db.commit()
    db.refresh(assignment)
    return assignment


def revoke_assignment(
    admin_id: str,
    educator_id: str,
    assignment_id: str,
    db: Session,
) -> None:
    """Revoke an educator class assignment. Immediate effect on next request."""
    assignment = (
        db.query(EducatorClassAssignment)
        .filter(
            EducatorClassAssignment.id == assignment_id,
            EducatorClassAssignment.educator_id == educator_id,
        )
        .first()
    )
    if not assignment:
        raise NotFoundError("Assignment not found", code="ASSIGNMENT_NOT_FOUND")

    if not assignment.active:
        raise ConflictError("Assignment is already revoked", code="ALREADY_REVOKED")

    now = utcnow()
    assignment.active = False
    assignment.revoked_at = now

    audit = AdminAuditEvent(
        actor_admin_id=admin_id,
        action="revoke_scope",
        target_type="assignment",
        target_id=assignment.id,
        metadata_json={"educator_id": educator_id},
    )
    db.add(audit)
    db.commit()


def get_educator_assignments(
    educator_id: str,
    db: Session,
) -> List[EducatorClassAssignment]:
    """Retrieve all assignments for an educator."""
    return (
        db.query(EducatorClassAssignment)
        .filter(EducatorClassAssignment.educator_id == educator_id)
        .order_by(EducatorClassAssignment.created_at.desc())
        .all()
    )
