"""API integration tests for Educator Analytics and Student Drill-down.

Conforms to Specification v3.0 Sections 11.0, 19.4, 19.5, 19.6, 19.8.
"""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password
from app.db.seed import seed_curriculum
from app.models.auth import (
    AdministratorAccount,
    Class,
    Educator,
    EducatorClassAssignment,
    Section,
)
from app.models.curriculum import Concept
from app.models.engine import StudentConceptMastery
from app.models.session import (
    DiagnosisSnapshot,
    LearningCompletion,
    Session as AssessmentSession,
    Student,
)


@pytest.fixture
def analytics_test_env(db_session: Session):
    """Seed curriculum and create classes, sections, students, sessions, and educator assignments."""
    seed_curriculum(db_session)

    admin = AdministratorAccount(
        id="admin_analytics",
        email="admin@univ.edu",
        password_hash=hash_password("AdminPass123!"),
        display_name="University Admin",
    )
    db_session.add(admin)

    # Approved educator
    educator = Educator(
        id="edu_db_prof",
        email="prof.clodd@univ.edu",
        password_hash=hash_password("ProfPass123!"),
        display_name="Prof. Codd",
        status="approved",
        approved_by_admin_id=admin.id,
    )
    db_session.add(educator)

    # Classes & Sections
    cls_db = Class(id="class_cs301", name="Database Systems", code="CS301")
    cls_os = Class(id="class_cs302", name="Operating Systems", code="CS302")
    db_session.add_all([cls_db, cls_os])
    db_session.flush()

    sec_db1 = Section(id="sec_cs301_1", class_id=cls_db.id, name="Section 1", code="S1")
    sec_db2 = Section(id="sec_cs301_2", class_id=cls_db.id, name="Section 2", code="S2")
    sec_os1 = Section(id="sec_cs302_1", class_id=cls_os.id, name="Section 1", code="S1")
    db_session.add_all([sec_db1, sec_db2, sec_os1])
    db_session.flush()

    # Students
    # CS301 Section 1: Alice (completed diagnostic), Bob (no completed diagnostic)
    stu_alice = Student(id="stu_alice", name="Alice", email="alice@univ.edu", class_id=cls_db.id, section_id=sec_db1.id)
    stu_bob = Student(id="stu_bob", name="Bob", email="bob@univ.edu", class_id=cls_db.id, section_id=sec_db1.id)
    # CS301 Section 2: Charlie (completed diagnostic)
    stu_charlie = Student(id="stu_charlie", name="Charlie", email="charlie@univ.edu", class_id=cls_db.id, section_id=sec_db2.id)
    # CS302 (OS): David (completed diagnostic in different class)
    stu_david = Student(id="stu_david", name="David", email="david@univ.edu", class_id=cls_os.id, section_id=sec_os1.id)
    db_session.add_all([stu_alice, stu_bob, stu_charlie, stu_david])
    db_session.flush()

    # Completed diagnostic session for Alice
    now = datetime.now(timezone.utc)
    sess_alice = AssessmentSession(
        id="sess_alice_diag",
        student_id=stu_alice.id,
        kind="diagnostic",
        status="completed",
        answered_count=12,
        started_at=now,
        completed_at=now,
    )
    # In-progress session for Bob (unfinished - must NOT count as completed diagnosis)
    sess_bob = AssessmentSession(
        id="sess_bob_active",
        student_id=stu_bob.id,
        kind="diagnostic",
        status="active",
        answered_count=4,
        started_at=now,
    )
    # Completed diagnostic session for Charlie
    sess_charlie = AssessmentSession(
        id="sess_charlie_diag",
        student_id=stu_charlie.id,
        kind="diagnostic",
        status="completed",
        answered_count=10,
        started_at=now,
        completed_at=now,
    )
    db_session.add_all([sess_alice, sess_bob, sess_charlie])
    db_session.flush()

    # Snapshots for Alice
    snap_a1 = DiagnosisSnapshot(
        session_id=sess_alice.id,
        student_id=stu_alice.id,
        concept_id="D01",
        mastery_estimate=0.85,
        direct_estimate=0.85,
        status="mastered",
        ready=True,
    )
    snap_a2 = DiagnosisSnapshot(
        session_id=sess_alice.id,
        student_id=stu_alice.id,
        concept_id="D08",
        mastery_estimate=0.25,
        direct_estimate=0.25,
        status="confirmed_gap",
        ready=False,
        likely_cause="misconception",
    )
    # Snapshots for Charlie
    snap_c1 = DiagnosisSnapshot(
        session_id=sess_charlie.id,
        student_id=stu_charlie.id,
        concept_id="D01",
        mastery_estimate=0.75,
        direct_estimate=0.75,
        status="mastered",
        ready=True,
    )
    snap_c2 = DiagnosisSnapshot(
        session_id=sess_charlie.id,
        student_id=stu_charlie.id,
        concept_id="D08",
        mastery_estimate=0.30,
        direct_estimate=0.30,
        status="suspected_gap",
        ready=False,
    )
    db_session.add_all([snap_a1, snap_a2, snap_c1, snap_c2])

    # Mastery rows for Alice and Charlie
    m_a1 = StudentConceptMastery(
        student_id=stu_alice.id,
        concept_id="D01",
        epoch_index=0,
        mastery_estimate=0.85,
        direct_estimate=0.85,
        status="mastered",
        ready=True,
        n_direct_correct_unassisted=3,
    )
    m_a2 = StudentConceptMastery(
        student_id=stu_alice.id,
        concept_id="D08",
        epoch_index=0,
        mastery_estimate=0.25,
        direct_estimate=0.25,
        status="confirmed_gap",
        ready=False,
        n_direct_incorrect=3,
    )
    m_c1 = StudentConceptMastery(
        student_id=stu_charlie.id,
        concept_id="D01",
        epoch_index=0,
        mastery_estimate=0.75,
        direct_estimate=0.75,
        status="mastered",
        ready=True,
        n_direct_correct_unassisted=2,
    )
    m_c2 = StudentConceptMastery(
        student_id=stu_charlie.id,
        concept_id="D08",
        epoch_index=0,
        mastery_estimate=0.30,
        direct_estimate=0.30,
        status="suspected_gap",
        ready=False,
        n_direct_incorrect=2,
    )
    db_session.add_all([m_a1, m_a2, m_c1, m_c2])

    # Assignment: Educator is assigned specifically to Section 1 of CS301
    asgn_s1 = EducatorClassAssignment(
        id="asgn_edu_s1",
        educator_id=educator.id,
        class_id=cls_db.id,
        section_id=sec_db1.id,  # Specific to S1
        active=True,
        created_by_admin_id=admin.id,
    )
    db_session.add(asgn_s1)
    db_session.commit()

    return {
        "admin": admin,
        "educator": educator,
        "class_db": cls_db,
        "class_os": cls_os,
        "sec_db1": sec_db1,
        "sec_db2": sec_db2,
        "stu_alice": stu_alice,
        "stu_bob": stu_bob,
        "stu_charlie": stu_charlie,
        "stu_david": stu_david,
        "assignment_s1": asgn_s1,
    }


def test_section_specific_analytics_and_denominators(client: TestClient, db_session: Session, analytics_test_env):
    """Analytics for Section 1 contains only Section 1 students (Alice, Bob), excluding Charlie (S2)."""
    env = analytics_test_env
    token = create_access_token({"sub": env["educator"].id, "role": "educator"})
    headers = {"Authorization": f"Bearer {token}"}

    # Request analytics for CS301 (Section 1)
    res = client.get(
        f"/api/v1/educators/me/classes/{env['class_db'].id}/analytics?section_id={env['sec_db1'].id}",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["class_id"] == env["class_db"].id
    assert data["section_id"] == env["sec_db1"].id
    assert data["total_students"] == 2  # Alice and Bob
    assert data["assessed_students"] == 1  # Alice only (Bob's diagnostic is unfinished)
    assert data["diagnostic_completion_rate"] == 0.5  # 1 / 2

    # Verify concept status distribution uses assessed_students denominator
    d01_dist = next(d for d in data["concepts_status_distribution"] if d["concept_id"] == "D01")
    assert d01_dist["mastered"] == 1
    assert d01_dist["mastered_rate"] == 1.0  # 1 / 1

    d08_dist = next(d for d in data["concepts_status_distribution"] if d["concept_id"] == "D08")
    assert d08_dist["confirmed_gap"] == 1
    assert d08_dist["confirmed_gap_rate"] == 1.0  # 1 / 1


def test_section_boundary_denies_unassigned_section(client: TestClient, analytics_test_env):
    """Educator assigned only to Section 1 cannot query Section 2 analytics or unassigned class."""
    env = analytics_test_env
    token = create_access_token({"sub": env["educator"].id, "role": "educator"})
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt Section 2 in same class
    res_s2 = client.get(
        f"/api/v1/educators/me/classes/{env['class_db'].id}/analytics?section_id={env['sec_db2'].id}",
        headers=headers,
    )
    assert res_s2.status_code == 403
    assert res_s2.json()["error"]["code"] == "SCOPE_UNAUTHORIZED"

    # Attempt another class (CS302)
    res_os = client.get(
        f"/api/v1/educators/me/classes/{env['class_os'].id}/analytics",
        headers=headers,
    )
    assert res_os.status_code == 403


def test_class_wide_grant_aggregates_all_sections(client: TestClient, db_session: Session, analytics_test_env):
    """When educator has a class-wide grant (section_id=None), analytics combines S1 and S2."""
    env = analytics_test_env
    # Upgrade educator assignment to class-wide
    env["assignment_s1"].section_id = None
    db_session.commit()

    token = create_access_token({"sub": env["educator"].id, "role": "educator"})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(
        f"/api/v1/educators/me/classes/{env['class_db'].id}/analytics",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_students"] == 3  # Alice (S1), Bob (S1), Charlie (S2)
    assert data["assessed_students"] == 2  # Alice and Charlie
    assert round(data["diagnostic_completion_rate"], 2) == 0.67

    # D01: 2 mastered (Alice + Charlie)
    d01_dist = next(d for d in data["concepts_status_distribution"] if d["concept_id"] == "D01")
    assert d01_dist["mastered"] == 2
    assert d01_dist["mastered_rate"] == 1.0


def test_empty_class_analytics_honest_representation(client: TestClient, db_session: Session, analytics_test_env):
    """Empty class with 0 enrolled students returns honest 0 counts and rates without errors."""
    env = analytics_test_env
    empty_class = Class(id="class_empty", name="Seminar", code="CS999")
    db_session.add(empty_class)
    db_session.flush()

    asgn_empty = EducatorClassAssignment(
        id="asgn_empty",
        educator_id=env["educator"].id,
        class_id=empty_class.id,
        section_id=None,
        active=True,
        created_by_admin_id=env["admin"].id,
    )
    db_session.add(asgn_empty)
    db_session.commit()

    token = create_access_token({"sub": env["educator"].id, "role": "educator"})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(
        f"/api/v1/educators/me/classes/{empty_class.id}/analytics",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_students"] == 0
    assert data["assessed_students"] == 0
    assert data["diagnostic_completion_rate"] == 0.0
    assert len(data["common_root_gaps"]) == 0


def test_authorized_students_pagination_and_scoping(client: TestClient, analytics_test_env):
    """GET /educators/me/students returns only authorized students with validated pagination."""
    env = analytics_test_env
    token = create_access_token({"sub": env["educator"].id, "role": "educator"})
    headers = {"Authorization": f"Bearer {token}"}

    # Query with default pagination (Educator assigned to S1 only)
    res = client.get("/api/v1/educators/me/students?page=1&page_size=10", headers=headers)
    assert res.status_code == 200
    data = res.json()
    student_ids = [item["id"] for item in data["items"]]
    assert "stu_alice" in student_ids
    assert "stu_bob" in student_ids
    # Charlie (S2) and David (CS302) must NOT be present
    assert "stu_charlie" not in student_ids
    assert "stu_david" not in student_ids
    assert data["total"] == 2

    # Query parameter narrowing
    res_narrow = client.get(
        f"/api/v1/educators/me/students?class_id={env['class_db'].id}&section_id={env['sec_db1'].id}",
        headers=headers,
    )
    assert res_narrow.status_code == 200
    assert res_narrow.json()["total"] == 2

    # Attempting to query unauthorized section returns 403
    res_broaden = client.get(
        f"/api/v1/educators/me/students?section_id={env['sec_db2'].id}",
        headers=headers,
    )
    assert res_broaden.status_code == 403


def test_student_diagnosis_drilldown_authorized_and_denied(client: TestClient, analytics_test_env):
    """GET /educators/me/students/{id}/diagnosis returns finalized diagnosis or rejects unauthorized."""
    env = analytics_test_env
    token = create_access_token({"sub": env["educator"].id, "role": "educator"})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Authorized student with completed diagnostic (Alice)
    res_alice = client.get(f"/api/v1/educators/me/students/{env['stu_alice'].id}/diagnosis", headers=headers)
    assert res_alice.status_code == 200
    data_alice = res_alice.json()
    assert data_alice["student_id"] == env["stu_alice"].id
    assert len(data_alice["root_gaps"]) >= 1

    # 2. Authorized student with NO completed diagnostic (Bob) -> 404
    res_bob = client.get(f"/api/v1/educators/me/students/{env['stu_bob'].id}/diagnosis", headers=headers)
    assert res_bob.status_code == 404
    assert res_bob.json()["error"]["code"] == "DIAGNOSIS_NOT_FOUND"

    # 3. Unauthorized student in another section (Charlie) -> 403
    res_charlie = client.get(f"/api/v1/educators/me/students/{env['stu_charlie'].id}/diagnosis", headers=headers)
    assert res_charlie.status_code == 403
    assert res_charlie.json()["error"]["code"] == "SCOPE_UNAUTHORIZED"

    # 4. Unauthorized student in another class (David) -> 403
    res_david = client.get(f"/api/v1/educators/me/students/{env['stu_david'].id}/diagnosis", headers=headers)
    assert res_david.status_code == 403


def test_student_progress_drilldown(client: TestClient, db_session: Session, analytics_test_env):
    """GET /educators/me/students/{id}/progress returns session history, concept status, and learning completion."""
    env = analytics_test_env
    token = create_access_token({"sub": env["educator"].id, "role": "educator"})
    headers = {"Authorization": f"Bearer {token}"}

    # Record learning completion for Alice
    comp = LearningCompletion(student_id=env["stu_alice"].id, concept_id="D01")
    db_session.add(comp)
    db_session.commit()

    res = client.get(f"/api/v1/educators/me/students/{env['stu_alice'].id}/progress", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == env["stu_alice"].id
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["kind"] == "diagnostic"

    # Check concepts progress
    d01_progress = next(p for p in data["concepts_progress"] if p["concept_id"] == "D01")
    assert d01_progress["learning_completed"] is True


def test_student_changes_section_live_isolation(client: TestClient, db_session: Session, analytics_test_env):
    """If a student moves from Section 1 to Section 2, the Section 1 educator immediately loses access."""
    env = analytics_test_env
    token = create_access_token({"sub": env["educator"].id, "role": "educator"})
    headers = {"Authorization": f"Bearer {token}"}

    # Alice is in S1 -> access allowed
    res1 = client.get(f"/api/v1/educators/me/students/{env['stu_alice'].id}/diagnosis", headers=headers)
    assert res1.status_code == 200

    # Administrator or system transfers Alice to Section 2
    env["stu_alice"].section_id = env["sec_db2"].id
    db_session.commit()

    # Next request immediately fails with 403 Forbidden!
    res2 = client.get(f"/api/v1/educators/me/students/{env['stu_alice'].id}/diagnosis", headers=headers)
    assert res2.status_code == 403
    assert res2.json()["error"]["code"] == "SCOPE_UNAUTHORIZED"


def test_immediate_revocation_on_analytics_endpoints(client: TestClient, db_session: Session, analytics_test_env):
    """Suspending an educator or revoking an assignment immediately blocks analytics on next request."""
    env = analytics_test_env
    token = create_access_token({"sub": env["educator"].id, "role": "educator"})
    headers = {"Authorization": f"Bearer {token}"}

    # Access permitted initially
    res1 = client.get(f"/api/v1/educators/me/students/{env['stu_alice'].id}/diagnosis", headers=headers)
    assert res1.status_code == 200

    # Revoke assignment
    env["assignment_s1"].active = False
    db_session.commit()

    # Next request immediately fails with 403 Forbidden
    res2 = client.get(f"/api/v1/educators/me/students/{env['stu_alice'].id}/diagnosis", headers=headers)
    assert res2.status_code == 403

    # Suspend educator
    env["educator"].status = "suspended"
    db_session.commit()

    res3 = client.get(f"/api/v1/educators/me/classes/{env['class_db'].id}/analytics", headers=headers)
    assert res3.status_code == 403
    assert res3.json()["error"]["code"] == "EDUCATOR_NOT_APPROVED"
