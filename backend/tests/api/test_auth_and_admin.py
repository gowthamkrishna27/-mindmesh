"""API integration tests for educator registration, authentication, admin workflows, and immediate revocation.

Conforms to Specification v3.0 Sections 11.0, 19.1-19.8.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password
from app.models.auth import (
    AdminAuditEvent,
    AdministratorAccount,
    Class,
    Educator,
    EducatorClassAssignment,
    Section,
)


def test_educator_registration_success(client: TestClient):
    """Test educator self-registration creates pending account without exposing hash."""
    payload = {
        "email": "NewEducator@University.EDU",
        "password": "SecurePassword123!",
        "display_name": "Dr. Grace Hopper",
    }
    response = client.post("/api/v1/educators/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "neweducator@university.edu"  # Normalized to lowercase
    assert data["display_name"] == "Dr. Grace Hopper"
    assert data["status"] == "pending"
    assert "password" not in data
    assert "password_hash" not in data


def test_educator_registration_duplicate_email(client: TestClient):
    """Prevent duplicate educator registrations and return 409."""
    payload = {
        "email": "duplicate@test.org",
        "password": "Password123!",
        "display_name": "First Register",
    }
    res1 = client.post("/api/v1/educators/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/educators/register", json=payload)
    assert res2.status_code == 409
    assert res2.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_educator_registration_validation(client: TestClient):
    """Reject invalid email, short password, or client-injected role fields."""
    # Short password
    res = client.post(
        "/api/v1/educators/register",
        json={"email": "valid@test.org", "password": "short", "display_name": "Name"},
    )
    assert res.status_code == 422

    # Invalid email
    res = client.post(
        "/api/v1/educators/register",
        json={"email": "notanemail", "password": "LongPassword123!", "display_name": "Name"},
    )
    assert res.status_code == 422

    # Extra role field forbidden
    res = client.post(
        "/api/v1/educators/register",
        json={
            "email": "hacker@test.org",
            "password": "LongPassword123!",
            "display_name": "Name",
            "role": "administrator",
        },
    )
    assert res.status_code == 422


def test_login_flow(client: TestClient, db_session: Session):
    """Test login for educator and administrator, verifying roles and constant-time rejection."""
    # Seed admin and educator
    admin = AdministratorAccount(
        id="admin_test",
        email="admin@test.org",
        password_hash=hash_password("AdminPass123!"),
        display_name="Admin Test",
    )
    educator = Educator(
        id="edu_test",
        email="edu@test.org",
        password_hash=hash_password("EduPass123!"),
        display_name="Educator Test",
        status="pending",
    )
    db_session.add_all([admin, educator])
    db_session.commit()

    # Admin login
    res_admin = client.post(
        "/api/v1/auth/login",
        json={"email": "ADMIN@TEST.ORG", "password": "AdminPass123!"},
    )
    assert res_admin.status_code == 200
    data_admin = res_admin.json()
    assert data_admin["role"] == "administrator"
    assert "access_token" in data_admin

    # Educator login
    res_edu = client.post(
        "/api/v1/auth/login",
        json={"email": "edu@test.org", "password": "EduPass123!"},
    )
    assert res_edu.status_code == 200
    data_edu = res_edu.json()
    assert data_edu["role"] == "educator"
    assert "access_token" in data_edu

    # Invalid password
    res_bad_pw = client.post(
        "/api/v1/auth/login",
        json={"email": "edu@test.org", "password": "WrongPassword!"},
    )
    assert res_bad_pw.status_code == 401
    assert res_bad_pw.json()["error"]["code"] == "INVALID_CREDENTIALS"

    # Non-existent user
    res_bad_user = client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@test.org", "password": "AnyPassword123!"},
    )
    assert res_bad_user.status_code == 401


def test_pending_educator_access_restrictions(client: TestClient, db_session: Session):
    """Pending educators can check their status but cannot access assignments or data."""
    educator = Educator(
        id="pending_edu",
        email="pending@test.org",
        password_hash=hash_password("Pass1234!"),
        display_name="Pending Teacher",
        status="pending",
    )
    db_session.add(educator)
    db_session.commit()

    token = create_access_token({"sub": educator.id, "role": "educator"})
    headers = {"Authorization": f"Bearer {token}"}

    # Can view own profile
    res_me = client.get("/api/v1/educators/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["status"] == "pending"

    # Cannot view assignments (403 Forbidden)
    res_asgn = client.get("/api/v1/educators/me/assignments", headers=headers)
    assert res_asgn.status_code == 403
    assert res_asgn.json()["error"]["code"] == "EDUCATOR_NOT_APPROVED"

    # Cannot access admin endpoints (403 Forbidden)
    res_admin = client.get("/api/v1/admin/educators", headers=headers)
    assert res_admin.status_code == 403


def test_admin_approval_and_assignment_workflow(client: TestClient, db_session: Session):
    """Full admin workflow: list pending, approve, assign class/section, inspect, revoke."""
    admin = AdministratorAccount(
        id="admin_1",
        email="admin@school.org",
        password_hash=hash_password("AdminPass123!"),
        display_name="School Admin",
    )
    educator = Educator(
        id="edu_1",
        email="edu@school.org",
        password_hash=hash_password("EduPass123!"),
        display_name="Prof Turing",
        status="pending",
    )
    cls = Class(id="cls_db", name="Databases", code="CS101")
    sec = Section(id="sec_1", class_id=cls.id, name="Morning", code="M1")
    db_session.add_all([admin, educator, cls, sec])
    db_session.commit()

    admin_token = create_access_token({"sub": admin.id, "role": "administrator"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    edu_token = create_access_token({"sub": educator.id, "role": "educator"})
    edu_headers = {"Authorization": f"Bearer {edu_token}"}

    # 1. Admin lists pending educators
    res_list = client.get("/api/v1/admin/educators?status=pending", headers=admin_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1
    assert res_list.json()[0]["id"] == educator.id

    # 2. Admin approves educator
    res_appr = client.post(f"/api/v1/admin/educators/{educator.id}/approve", headers=admin_headers)
    assert res_appr.status_code == 200
    assert res_appr.json()["status"] == "approved"
    assert res_appr.json()["approved_by_admin_id"] == admin.id

    # Cannot approve already approved educator
    res_reappr = client.post(f"/api/v1/admin/educators/{educator.id}/approve", headers=admin_headers)
    assert res_reappr.status_code == 409

    # 3. Now approved educator can view /assignments (currently empty)
    res_my_asgn = client.get("/api/v1/educators/me/assignments", headers=edu_headers)
    assert res_my_asgn.status_code == 200
    assert len(res_my_asgn.json()) == 0

    # 4. Admin assigns class and section
    asgn_payload = {"class_id": cls.id, "section_id": sec.id}
    res_asgn = client.post(
        f"/api/v1/admin/educators/{educator.id}/assignments",
        json=asgn_payload,
        headers=admin_headers,
    )
    assert res_asgn.status_code == 201
    asgn_data = res_asgn.json()
    assignment_id = asgn_data["id"]
    assert asgn_data["active"] is True

    # Duplicate active assignment rejected
    res_dup = client.post(
        f"/api/v1/admin/educators/{educator.id}/assignments",
        json=asgn_payload,
        headers=admin_headers,
    )
    assert res_dup.status_code == 409

    # 5. Educator now sees the assignment
    res_my_asgn2 = client.get("/api/v1/educators/me/assignments", headers=edu_headers)
    assert res_my_asgn2.status_code == 200
    assert len(res_my_asgn2.json()) == 1
    assert res_my_asgn2.json()[0]["class_id"] == cls.id

    # 6. Admin inspects assignments
    res_inspect = client.get(
        f"/api/v1/admin/educators/{educator.id}/assignments",
        headers=admin_headers,
    )
    assert res_inspect.status_code == 200
    assert len(res_inspect.json()) == 1

    # 7. Admin revokes assignment
    res_del = client.delete(
        f"/api/v1/admin/educators/{educator.id}/assignments/{assignment_id}",
        headers=admin_headers,
    )
    assert res_del.status_code == 204

    # Educator now sees 0 active assignments on next request
    res_my_asgn3 = client.get("/api/v1/educators/me/assignments", headers=edu_headers)
    assert len(res_my_asgn3.json()) == 0

    # Verify audit events recorded
    audit_events = db_session.query(AdminAuditEvent).filter(AdminAuditEvent.actor_admin_id == admin.id).all()
    actions = [evt.action for evt in audit_events]
    assert "approve_educator" in actions
    assert "assign_scope" in actions
    assert "revoke_scope" in actions


def test_immediate_revocation_on_suspension(client: TestClient, db_session: Session):
    """When an administrator suspends an approved educator, the next protected request is immediately blocked."""
    admin = AdministratorAccount(
        id="admin_revoker",
        email="revoker@school.org",
        password_hash=hash_password("AdminPass123!"),
        display_name="Revoker Admin",
    )
    educator = Educator(
        id="edu_to_suspend",
        email="suspendee@school.org",
        password_hash=hash_password("Pass1234!"),
        display_name="Teacher X",
        status="approved",
        approved_by_admin_id=admin.id,
    )
    db_session.add_all([admin, educator])
    db_session.commit()

    admin_token = create_access_token({"sub": admin.id, "role": "administrator"})
    edu_token = create_access_token({"sub": educator.id, "role": "educator"})
    edu_headers = {"Authorization": f"Bearer {edu_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Request succeeds while approved
    res_before = client.get("/api/v1/educators/me/assignments", headers=edu_headers)
    assert res_before.status_code == 200

    # Admin suspends educator
    res_susp = client.post(
        f"/api/v1/admin/educators/{educator.id}/suspend",
        headers=admin_headers,
    )
    assert res_susp.status_code == 200
    assert res_susp.json()["status"] == "suspended"

    # On next request, existing token fails immediately with 403 Forbidden!
    res_after = client.get("/api/v1/educators/me/assignments", headers=edu_headers)
    assert res_after.status_code == 403
    assert res_after.json()["error"]["code"] == "EDUCATOR_NOT_APPROVED"


def test_invalid_and_forged_tokens_rejected(client: TestClient):
    """Requests with missing, invalid, or forged authentication headers are rejected."""
    # Missing header
    res_no_auth = client.get("/api/v1/educators/me")
    assert res_no_auth.status_code == 401

    # Malformed header
    res_bad_header = client.get("/api/v1/educators/me", headers={"Authorization": "Token 12345"})
    assert res_bad_header.status_code == 401

    # Tampered token
    res_tampered = client.get("/api/v1/educators/me", headers={"Authorization": "Bearer not.a.valid.jwt"})
    assert res_tampered.status_code == 401


def test_admin_reject_educator(client: TestClient, db_session: Session):
    """Admin can reject a pending educator application."""
    admin = AdministratorAccount(
        id="admin_rej",
        email="admin_rej@school.org",
        password_hash=hash_password("Pass123!"),
        display_name="Admin",
    )
    educator = Educator(
        id="edu_rej",
        email="edu_rej@school.org",
        password_hash=hash_password("Pass123!"),
        display_name="Rejected Teacher",
        status="pending",
    )
    db_session.add_all([admin, educator])
    db_session.commit()

    admin_token = create_access_token({"sub": admin.id, "role": "administrator"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    res_rej = client.post(f"/api/v1/admin/educators/{educator.id}/reject", headers=admin_headers)
    assert res_rej.status_code == 200
    assert res_rej.json()["status"] == "rejected"

    # Rejecting an already rejected educator returns 409
    res_rerej = client.post(f"/api/v1/admin/educators/{educator.id}/reject", headers=admin_headers)
    assert res_rerej.status_code == 409


def test_admin_assignment_validation_failures(client: TestClient, db_session: Session):
    """Verify that assignments to nonexistent classes, wrong sections, or pending educators fail."""
    admin = AdministratorAccount(
        id="admin_v",
        email="admin_v@school.org",
        password_hash=hash_password("Pass123!"),
        display_name="Admin",
    )
    edu_pending = Educator(
        id="edu_p",
        email="edu_p@school.org",
        password_hash=hash_password("Pass123!"),
        display_name="Pending Teacher",
        status="pending",
    )
    cls1 = Class(id="c1", name="Class 1", code="C1")
    cls2 = Class(id="c2", name="Class 2", code="C2")
    sec2 = Section(id="s2", class_id=cls2.id, name="Sec 2", code="S2")
    db_session.add_all([admin, edu_pending, cls1, cls2, sec2])
    db_session.commit()

    admin_token = create_access_token({"sub": admin.id, "role": "administrator"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Cannot assign class to pending educator
    res1 = client.post(
        f"/api/v1/admin/educators/{edu_pending.id}/assignments",
        json={"class_id": cls1.id},
        headers=admin_headers,
    )
    assert res1.status_code == 400
    assert res1.json()["error"]["code"] == "EDUCATOR_NOT_APPROVED"

    # Approve educator
    edu_pending.status = "approved"
    db_session.commit()

    # 2. Cannot assign nonexistent class
    res2 = client.post(
        f"/api/v1/admin/educators/{edu_pending.id}/assignments",
        json={"class_id": "nonexistent_class"},
        headers=admin_headers,
    )
    assert res2.status_code == 404
    assert res2.json()["error"]["code"] == "CLASS_NOT_FOUND"

    # 3. Cannot assign section belonging to a different class
    res3 = client.post(
        f"/api/v1/admin/educators/{edu_pending.id}/assignments",
        json={"class_id": cls1.id, "section_id": sec2.id},
        headers=admin_headers,
    )
    assert res3.status_code == 400
    assert res3.json()["error"]["code"] == "SECTION_CLASS_MISMATCH"
