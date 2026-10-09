"""Assigned-Scope Authorization Service for MindMesh Educators.

Conforms to Specification v3.0 Sections 11.0, 19.3, 19.4, 19.6:
- Fails closed if the identity, assignment, or scope cannot be validated.
- Denies cross-class and cross-section access.
- Immediate revocation enforcement on live database state.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.errors import ForbiddenError, NotFoundError
from app.models.auth import Class, Educator, EducatorClassAssignment, Section
from app.models.session import Student


def get_educator_active_assignments(
    educator_id: str,
    db: Session,
) -> List[EducatorClassAssignment]:
    """Retrieve all active class/section assignments for an educator."""
    return (
        db.query(EducatorClassAssignment)
        .filter(
            EducatorClassAssignment.educator_id == educator_id,
            EducatorClassAssignment.active.is_(True),
        )
        .all()
    )


def verify_educator_scope(
    educator_id: str,
    class_id: str,
    section_id: Optional[str] = None,
    db: Session = None,
) -> bool:
    """Check if educator has an active assignment granting access to the class and section.

    Assignment semantics:
    - section_id is None in assignment -> class-wide grant, covers all sections in that class.
    - section_id is specific -> grants access only to that specific section.
    """
    assignments = (
        db.query(EducatorClassAssignment)
        .filter(
            EducatorClassAssignment.educator_id == educator_id,
            EducatorClassAssignment.class_id == class_id,
            EducatorClassAssignment.active.is_(True),
        )
        .all()
    )

    if not assignments:
        return False

    for assignment in assignments:
        # Class-wide grant
        if assignment.section_id is None:
            return True
        # Section-specific grant matching requested section
        if section_id and assignment.section_id == section_id:
            return True

    return False


def verify_student_access(
    educator_id: str,
    student_id: str,
    db: Session,
) -> Student:
    """Verify that an educator has active assignment authorization for a student.

    Returns the Student model if authorized, or raises ForbiddenError/NotFoundError.
    Fails closed.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise NotFoundError("Student record not found", code="STUDENT_NOT_FOUND")

    # If student is not assigned to any class, no educator has access
    if not student.class_id:
        raise ForbiddenError(
            "Student does not belong to any assigned class",
            code="SCOPE_UNAUTHORIZED",
        )

    # Check educator scope against student's class and section
    has_access = verify_educator_scope(
        educator_id=educator_id,
        class_id=student.class_id,
        section_id=student.section_id,
        db=db,
    )

    if not has_access:
        raise ForbiddenError(
            "Access to student record outside assigned scope is forbidden",
            code="SCOPE_UNAUTHORIZED",
        )

    return student


def get_authorized_student_query(
    educator_id: str,
    class_id: Optional[str] = None,
    section_id: Optional[str] = None,
    db: Session = None,
):
    """Build an authorized SQLAlchemy query for students in educator's assigned scopes.

    Enforces scope restrictions directly at the query level before records are retrieved.
    Validates that optional client filters can only narrow, never broaden, the authorized set.
    """
    from sqlalchemy import and_, or_

    active_assignments = get_educator_active_assignments(educator_id=educator_id, db=db)
    if not active_assignments:
        raise ForbiddenError(
            "Educator has no active class or section assignments",
            code="NO_ACTIVE_ASSIGNMENTS",
        )

    # Resolve educator grants
    class_wide_classes = {a.class_id for a in active_assignments if a.section_id is None}
    section_grants = {(a.class_id, a.section_id) for a in active_assignments if a.section_id is not None}
    all_assigned_classes = class_wide_classes.union({c for (c, _) in section_grants})

    # Validate client class_id filter if provided
    if class_id:
        if class_id not in all_assigned_classes:
            raise ForbiddenError(
                "Requested class is outside educator's assigned scope",
                code="SCOPE_UNAUTHORIZED",
            )
        # Validate client section_id filter if provided
        if section_id:
            # Check if educator has access to (class_id, section_id)
            if class_id not in class_wide_classes and (class_id, section_id) not in section_grants:
                raise ForbiddenError(
                    "Requested section is outside educator's assigned scope",
                    code="SCOPE_UNAUTHORIZED",
                )
            return db.query(Student).filter(
                Student.class_id == class_id,
                Student.section_id == section_id,
            )
        else:
            # Filter by class_id only
            if class_id in class_wide_classes:
                return db.query(Student).filter(Student.class_id == class_id)
            else:
                allowed_sections = [s for (c, s) in section_grants if c == class_id]
                return db.query(Student).filter(
                    Student.class_id == class_id,
                    Student.section_id.in_(allowed_sections),
                )

    # Client did not specify class_id
    if section_id:
        # If client passed section_id without class_id, verify educator has access to this section in any assigned class
        matching_grants = [
            c for (c, s) in section_grants if s == section_id
        ]
        # Or class-wide grant where section belongs to that class
        sec_obj = db.query(Section).filter(Section.id == section_id).first()
        if not sec_obj:
            raise NotFoundError("Section not found", code="SECTION_NOT_FOUND")

        if sec_obj.class_id not in class_wide_classes and (sec_obj.class_id, section_id) not in section_grants:
            raise ForbiddenError(
                "Requested section is outside educator's assigned scope",
                code="SCOPE_UNAUTHORIZED",
            )
        return db.query(Student).filter(
            Student.class_id == sec_obj.class_id,
            Student.section_id == section_id,
        )

    # No filters provided: combine all active assignments with OR
    clauses = []
    for c in class_wide_classes:
        clauses.append(Student.class_id == c)

    for (c, s) in section_grants:
        if c not in class_wide_classes:
            clauses.append(and_(Student.class_id == c, Student.section_id == s))

    if not clauses:
        return db.query(Student).filter(False)

    return db.query(Student).filter(or_(*clauses))
