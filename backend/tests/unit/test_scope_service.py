"""Unit tests for assigned-scope authorization and student access isolation.

Conforms to Specification v3.0 Sections 11.0, 19.3, 19.4, 19.6, 19.8.
"""

import pytest
from sqlalchemy.orm import Session
from app.core.errors import ForbiddenError, NotFoundError
from app.models.auth import (
    AdministratorAccount,
    Class,
    Educator,
    EducatorClassAssignment,
    Section,
)
from app.models.session import Student
from app.services.scope_service import (
    get_educator_active_assignments,
    verify_educator_scope,
    verify_student_access,
)


@pytest.fixture
def scope_setup(db_session: Session):
    """Set up administrator, approved educator, classes, sections, and students."""
    admin = AdministratorAccount(
        id="admin_1",
        email="admin@test.org",
        password_hash="fakehash",
        display_name="Admin",
    )
    db_session.add(admin)

    educator = Educator(
        id="edu_1",
        email="edu@test.org",
        password_hash="fakehash",
        display_name="Prof Smith",
        status="approved",
        approved_by_admin_id=admin.id,
    )
    db_session.add(educator)

    cls_a = Class(id="class_a", name="Database Systems", code="CS301")
    cls_b = Class(id="class_b", name="Algorithms", code="CS302")
    db_session.add_all([cls_a, cls_b])
    db_session.flush()

    sec_a1 = Section(id="sec_a1", class_id=cls_a.id, name="Section 1", code="S1")
    sec_a2 = Section(id="sec_a2", class_id=cls_a.id, name="Section 2", code="S2")
    sec_b1 = Section(id="sec_b1", class_id=cls_b.id, name="Section 1", code="S1")
    db_session.add_all([sec_a1, sec_a2, sec_b1])
    db_session.flush()

    stu_a1 = Student(id="stu_a1", name="Alice", class_id=cls_a.id, section_id=sec_a1.id)
    stu_a2 = Student(id="stu_a2", name="Bob", class_id=cls_a.id, section_id=sec_a2.id)
    stu_b1 = Student(id="stu_b1", name="Charlie", class_id=cls_b.id, section_id=sec_b1.id)
    stu_unassigned = Student(id="stu_none", name="David", class_id=None, section_id=None)
    db_session.add_all([stu_a1, stu_a2, stu_b1, stu_unassigned])
    db_session.commit()

    return {
        "admin": admin,
        "educator": educator,
        "class_a": cls_a,
        "class_b": cls_b,
        "sec_a1": sec_a1,
        "sec_a2": sec_a2,
        "sec_b1": sec_b1,
        "stu_a1": stu_a1,
        "stu_a2": stu_a2,
        "stu_b1": stu_b1,
        "stu_none": stu_unassigned,
    }


def test_section_specific_assignment(db_session: Session, scope_setup):
    """Educator assigned only to Section A1 can access only Section A1."""
    env = scope_setup
    assignment = EducatorClassAssignment(
        id="asgn_1",
        educator_id=env["educator"].id,
        class_id=env["class_a"].id,
        section_id=env["sec_a1"].id,
        active=True,
        created_by_admin_id=env["admin"].id,
    )
    db_session.add(assignment)
    db_session.commit()

    # Scope checks
    assert verify_educator_scope(env["educator"].id, env["class_a"].id, env["sec_a1"].id, db=db_session) is True
    assert verify_educator_scope(env["educator"].id, env["class_a"].id, env["sec_a2"].id, db=db_session) is False
    assert verify_educator_scope(env["educator"].id, env["class_b"].id, env["sec_b1"].id, db=db_session) is False

    # Student access checks
    student = verify_student_access(env["educator"].id, env["stu_a1"].id, db=db_session)
    assert student.id == env["stu_a1"].id

    # Cross-section in same class is denied
    with pytest.raises(ForbiddenError):
        verify_student_access(env["educator"].id, env["stu_a2"].id, db=db_session)

    # Cross-class is denied
    with pytest.raises(ForbiddenError):
        verify_student_access(env["educator"].id, env["stu_b1"].id, db=db_session)


def test_class_wide_grant_covers_all_sections(db_session: Session, scope_setup):
    """Educator with section_id=None has a class-wide grant covering all sections of that class."""
    env = scope_setup
    assignment = EducatorClassAssignment(
        id="asgn_class_wide",
        educator_id=env["educator"].id,
        class_id=env["class_a"].id,
        section_id=None,  # Class-wide grant
        active=True,
        created_by_admin_id=env["admin"].id,
    )
    db_session.add(assignment)
    db_session.commit()

    # Allowed for both sections of class A
    assert verify_educator_scope(env["educator"].id, env["class_a"].id, env["sec_a1"].id, db=db_session) is True
    assert verify_educator_scope(env["educator"].id, env["class_a"].id, env["sec_a2"].id, db=db_session) is True
    # Still denied for class B
    assert verify_educator_scope(env["educator"].id, env["class_b"].id, env["sec_b1"].id, db=db_session) is False

    # Can access students in both Section A1 and Section A2
    assert verify_student_access(env["educator"].id, env["stu_a1"].id, db=db_session).id == env["stu_a1"].id
    assert verify_student_access(env["educator"].id, env["stu_a2"].id, db=db_session).id == env["stu_a2"].id

    # Denied for Class B student
    with pytest.raises(ForbiddenError):
        verify_student_access(env["educator"].id, env["stu_b1"].id, db=db_session)


def test_inactive_assignment_fails_closed(db_session: Session, scope_setup):
    """An inactive/revoked assignment immediately denies access."""
    env = scope_setup
    assignment = EducatorClassAssignment(
        id="asgn_inactive",
        educator_id=env["educator"].id,
        class_id=env["class_a"].id,
        section_id=env["sec_a1"].id,
        active=False,  # Revoked
        created_by_admin_id=env["admin"].id,
    )
    db_session.add(assignment)
    db_session.commit()

    assert verify_educator_scope(env["educator"].id, env["class_a"].id, env["sec_a1"].id, db=db_session) is False
    with pytest.raises(ForbiddenError):
        verify_student_access(env["educator"].id, env["stu_a1"].id, db=db_session)


def test_unassigned_student_and_nonexistent_student(db_session: Session, scope_setup):
    """Verify safe failure when querying students without classes or nonexistent IDs."""
    env = scope_setup
    assignment = EducatorClassAssignment(
        id="asgn_active",
        educator_id=env["educator"].id,
        class_id=env["class_a"].id,
        section_id=None,
        active=True,
        created_by_admin_id=env["admin"].id,
    )
    db_session.add(assignment)
    db_session.commit()

    # Student without class_id
    with pytest.raises(ForbiddenError):
        verify_student_access(env["educator"].id, env["stu_none"].id, db=db_session)

    # Nonexistent student
    with pytest.raises(NotFoundError):
        verify_student_access(env["educator"].id, "nonexistent_id", db=db_session)
