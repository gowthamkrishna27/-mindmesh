"""End-to-End Educator Registration, Approval, Assignment, and Immediate Revocation Journey.

Conforms to Specification v3.0 Sections 11.0, 19.1-19.8.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.bootstrap_admin import bootstrap_initial_admin
from app.db.seed import seed_curriculum
from app.models.auth import Class, Section
from app.models.session import Student


def test_complete_educator_journey(client: TestClient, db_session: Session):
    """Verify educator self-registration, pending isolation, admin approval, scope isolation, and immediate revocation."""
    # 1. Seed curriculum and setup test class with two sections
    seed_curriculum(db_session)
    cls = Class(id="cls_cs401", name="Advanced Databases", code="CS401")
    sec1 = Section(id="sec_401_a", class_id=cls.id, name="Morning", code="A")
    sec2 = Section(id="sec_401_b", class_id=cls.id, name="Evening", code="B")
    stu_a = Student(id="stu_sec_a", name="Alice", email="alice@test.org", class_id=cls.id, section_id=sec1.id)
    stu_b = Student(id="stu_sec_b", name="Bob", email="bob@test.org", class_id=cls.id, section_id=sec2.id)
    db_session.add_all([cls, sec1, sec2, stu_a, stu_b])
    db_session.commit()

    # 2. Bootstrap initial administrator
    admin = bootstrap_initial_admin(
        email="lead.admin@mindmesh.org",
        password="AdminSecurePassword123!",
        display_name="Lead Administrator",
        db=db_session,
    )
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"email": "lead.admin@mindmesh.org", "password": "AdminSecurePassword123!"},
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Educator self-registers
    res_reg = client.post(
        "/api/v1/educators/register",
        json={
            "email": "dr.smith@university.edu",
            "password": "SmithSecurePassword123!",
            "display_name": "Dr. John Smith",
        },
    )
    assert res_reg.status_code == 201
    educator_id = res_reg.json()["id"]
    assert res_reg.json()["status"] == "pending"

    # 4. Educator logs in
    edu_login = client.post(
        "/api/v1/auth/login",
        json={"email": "dr.smith@university.edu", "password": "SmithSecurePassword123!"},
    )
    assert edu_login.status_code == 200
    edu_token = edu_login.json()["access_token"]
    edu_headers = {"Authorization": f"Bearer {edu_token}"}

    # 5. Confirm pending educator is denied access to student data and assignments
    res_asgn_denied = client.get("/api/v1/educators/me/assignments", headers=edu_headers)
    assert res_asgn_denied.status_code == 403
    assert res_asgn_denied.json()["error"]["code"] == "EDUCATOR_NOT_APPROVED"

    res_stu_denied = client.get("/api/v1/educators/me/students", headers=edu_headers)
    assert res_stu_denied.status_code == 403

    # 6. Administrator approves educator
    res_appr = client.post(f"/api/v1/admin/educators/{educator_id}/approve", headers=admin_headers)
    assert res_appr.status_code == 200
    assert res_appr.json()["status"] == "approved"

    # 7. Approved educator with no assignment still has no students
    res_no_asgn_stu = client.get("/api/v1/educators/me/students", headers=edu_headers)
    assert res_no_asgn_stu.status_code == 403  # NO_ACTIVE_ASSIGNMENTS

    # 8. Administrator assigns educator to Section A only
    res_assign = client.post(
        f"/api/v1/admin/educators/{educator_id}/assignments",
        json={"class_id": cls.id, "section_id": sec1.id},
        headers=admin_headers,
    )
    assert res_assign.status_code == 201
    assignment_id = res_assign.json()["id"]

    # 9. Educator can now retrieve authorized analytics and students
    res_stu_auth = client.get("/api/v1/educators/me/students", headers=edu_headers)
    assert res_stu_auth.status_code == 200
    items = res_stu_auth.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == "stu_sec_a"  # Alice only

    res_analytics = client.get(
        f"/api/v1/educators/me/classes/{cls.id}/analytics?section_id={sec1.id}",
        headers=edu_headers,
    )
    assert res_analytics.status_code == 200
    assert res_analytics.json()["total_students"] == 1

    # 10. Verify Section B is inaccessible (fails closed)
    res_sec_b_analytics = client.get(
        f"/api/v1/educators/me/classes/{cls.id}/analytics?section_id={sec2.id}",
        headers=edu_headers,
    )
    assert res_sec_b_analytics.status_code == 403
    assert res_sec_b_analytics.json()["error"]["code"] == "SCOPE_UNAUTHORIZED"

    # 11. Administrator suspends the educator
    res_susp = client.post(f"/api/v1/admin/educators/{educator_id}/suspend", headers=admin_headers)
    assert res_susp.status_code == 200
    assert res_susp.json()["status"] == "suspended"

    # 12. Next protected request is immediately denied with 403
    res_next_req = client.get("/api/v1/educators/me/assignments", headers=edu_headers)
    assert res_next_req.status_code == 403
    assert res_next_req.json()["error"]["code"] == "EDUCATOR_NOT_APPROVED"

    res_next_analytics = client.get(
        f"/api/v1/educators/me/classes/{cls.id}/analytics?section_id={sec1.id}",
        headers=edu_headers,
    )
    assert res_next_analytics.status_code == 403
