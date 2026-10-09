"""API integration tests for student assessment session lifecycle.

Conforms strictly to Specification v3.0 Sections 6, 8, 11.1 - 11.5, 12, 13.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.seed import seed_curriculum
from app.models.curriculum import Question, QuestionOption
from app.models.engine import Response, StudentConceptMastery
from app.models.session import DiagnosisSnapshot, InteractionEvent, Session as AssessmentSession, Student


@pytest.fixture(autouse=True)
def setup_curriculum(db_session: Session):
    """Seed curriculum data into test database."""
    seed_curriculum(db_session)


def test_create_session_success(client: TestClient):
    """POST /sessions creates a new diagnostic assessment session with consent=True (Section 11.1)."""
    response = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers={"Authorization": "Bearer test_student_1"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["kind"] == "diagnostic"
    assert data["status"] == "active"
    assert data["question_limit"] == 12
    assert data["answered_count"] == 0


def test_create_session_consent_required(client: TestClient):
    """POST /sessions with consent=False or missing returns 400 CONSENT_REQUIRED (Section 11.1)."""
    response = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": False},
        headers={"Authorization": "Bearer test_student_1"},
    )
    assert response.status_code == 400
    err = response.json()["error"]
    assert err["code"] == "CONSENT_REQUIRED"


def test_create_session_invalid_kind(client: TestClient):
    """POST /sessions with invalid kind returns 422 VALIDATION_ERROR."""
    response = client.post(
        "/api/v1/sessions",
        json={"kind": "invalid_kind", "consent": True},
        headers={"Authorization": "Bearer test_student_1"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_session_retest_requires_diagnostic(client: TestClient):
    """POST /sessions with kind=retest without completed diagnostic returns 400 (Section 11.1)."""
    response = client.post(
        "/api/v1/sessions",
        json={"kind": "retest", "consent": True},
        headers={"Authorization": "Bearer student_no_diag"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "COMPLETED_DIAGNOSTIC_REQUIRED"


def test_create_session_practice_requires_concept(client: TestClient):
    """POST /sessions with kind=practice without concept_id returns 400 (Section 11.1)."""
    response = client.post(
        "/api/v1/sessions",
        json={"kind": "practice", "consent": True},
        headers={"Authorization": "Bearer test_student_1"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "CONCEPT_ID_REQUIRED"


def test_next_question_issuance_and_no_leakage(client: TestClient):
    """GET /sessions/{id}/next returns question without leaking answer key or explanations (Section 11.2)."""
    # 1. Create session
    create_res = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers={"Authorization": "Bearer test_student_leak"},
    )
    session_id = create_res.json()["session_id"]

    # 2. Get next question
    next_res = client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers={"Authorization": "Bearer test_student_leak"},
    )
    assert next_res.status_code == 200
    data = next_res.json()
    assert data["session_id"] == session_id
    assert data["status"] == "active"
    assert "question" in data
    q = data["question"]
    assert q is not None
    assert q["primary_concept_id"] == "D02"  # First baseline concept
    assert "options" in q
    assert len(q["options"]) == 4

    # CRITICAL: Verify NO answer-key or distractor-misconception leakage
    assert "correct_option_id" not in q
    assert "explanation" not in q
    for opt in q["options"]:
        assert "is_correct" not in opt
        assert "maps_to_concept_id" not in opt
        assert "misconception_code" not in opt
        assert "misconception_text" not in opt


def test_next_question_idempotency(client: TestClient):
    """GET /sessions/{id}/next is idempotent and returns the same unanswered question (Section 11.2)."""
    create_res = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers={"Authorization": "Bearer test_student_idem"},
    )
    session_id = create_res.json()["session_id"]

    first_res = client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers={"Authorization": "Bearer test_student_idem"},
    )
    second_res = client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers={"Authorization": "Bearer test_student_idem"},
    )

    assert first_res.status_code == 200
    assert second_res.status_code == 200
    assert first_res.json()["question"]["id"] == second_res.json()["question"]["id"]


def test_interaction_events_recording(client: TestClient):
    """POST /sessions/{id}/events validates and persists interaction events (Section 11.3)."""
    create_res = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers={"Authorization": "Bearer test_student_events"},
    )
    session_id = create_res.json()["session_id"]

    # Issue next question
    next_res = client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers={"Authorization": "Bearer test_student_events"},
    )
    question_id = next_res.json()["question"]["id"]

    # 1. Valid event
    ev1_res = client.post(
        f"/api/v1/sessions/{session_id}/events",
        json={
            "event_type": "question_displayed",
            "question_id": question_id,
            "payload": {"displayed_at": 100},
        },
        headers={"Authorization": "Bearer test_student_events"},
    )
    assert ev1_res.status_code == 200
    assert ev1_res.json()["event_type"] == "question_displayed"

    # 2. Option changed event
    ev2_res = client.post(
        f"/api/v1/sessions/{session_id}/events",
        json={
            "event_type": "option_changed",
            "question_id": question_id,
            "payload": {"from_option_id": None, "to_option_id": "A"},
        },
        headers={"Authorization": "Bearer test_student_events"},
    )
    assert ev2_res.status_code == 200

    # 3. Disallowed event type
    bad_type_res = client.post(
        f"/api/v1/sessions/{session_id}/events",
        json={
            "event_type": "arbitrary_custom_event",
            "payload": {},
        },
        headers={"Authorization": "Bearer test_student_events"},
    )
    assert bad_type_res.status_code == 400
    assert bad_type_res.json()["error"]["code"] == "INVALID_EVENT_TYPE"

    # 4. Question mismatch
    mismatch_res = client.post(
        f"/api/v1/sessions/{session_id}/events",
        json={
            "event_type": "option_changed",
            "question_id": "NON_ISSUED_QUESTION_XYZ",
            "payload": {},
        },
        headers={"Authorization": "Bearer test_student_events"},
    )
    assert mismatch_res.status_code == 400
    assert mismatch_res.json()["error"]["code"] == "QUESTION_MISMATCH"


def test_answer_submission_and_duplicate_prevention(client: TestClient, db_session: Session):
    """POST /sessions/{id}/answers evaluates answer, updates mastery, and prevents duplicates (Section 11.4)."""
    create_res = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers={"Authorization": "Bearer test_student_ans"},
    )
    session_id = create_res.json()["session_id"]

    # Issue next question
    next_res = client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers={"Authorization": "Bearer test_student_ans"},
    )
    question_data = next_res.json()["question"]
    question_id = question_data["id"]
    chosen_opt = question_data["options"][0]

    # Record some interaction events
    client.post(
        f"/api/v1/sessions/{session_id}/events",
        json={
            "event_type": "option_changed",
            "question_id": question_id,
            "payload": {"from_option_id": None, "to_option_id": chosen_opt["option_key"]},
        },
        headers={"Authorization": "Bearer test_student_ans"},
    )

    # Submit answer
    ans_res = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={
            "question_id": question_id,
            "selected_option_id": chosen_opt["id"],
            "confidence": "sure",
            "client_response_time_ms": 4500,
        },
        headers={"Authorization": "Bearer test_student_ans"},
    )
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert ans_data["session_id"] == session_id
    assert ans_data["status"] == "active"
    assert ans_data["progress"]["answered_count"] == 1
    # CRITICAL: Progress returned only, NO correctness or explanation!
    assert "is_correct" not in ans_data
    assert "explanation" not in ans_data

    # Verify Response was persisted in DB
    resp_row = db_session.query(Response).filter(Response.session_id == session_id).first()
    assert resp_row is not None
    assert resp_row.question_id == question_id
    assert resp_row.selected_option_key == chosen_opt["option_key"]

    # Verify mastery record was updated in DB
    mastery_d02 = (
        db_session.query(StudentConceptMastery)
        .filter(
            StudentConceptMastery.student_id == "test_student_ans",
            StudentConceptMastery.concept_id == "D02",
        )
        .first()
    )
    assert mastery_d02 is not None
    assert mastery_d02.n_direct_questions == 1

    # Attempt duplicate submission for same question: must return 409 CONFLICT
    dup_res = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={
            "question_id": question_id,
            "selected_option_id": chosen_opt["id"],
            "confidence": "sure",
        },
        headers={"Authorization": "Bearer test_student_ans"},
    )
    assert dup_res.status_code == 409
    assert dup_res.json()["error"]["code"] == "DUPLICATE_ANSWER"


def test_hint_event_enforces_assisted_flag(client: TestClient, db_session: Session):
    """Client cannot falsely claim assisted=False if hint_requested event was recorded (Section 11.4)."""
    create_res = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers={"Authorization": "Bearer test_student_hint"},
    )
    session_id = create_res.json()["session_id"]

    next_res = client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers={"Authorization": "Bearer test_student_hint"},
    )
    q_data = next_res.json()["question"]

    # Record hint event
    client.post(
        f"/api/v1/sessions/{session_id}/events",
        json={
            "event_type": "hint_requested",
            "question_id": q_data["id"],
            "payload": {"hint_level": 1},
        },
        headers={"Authorization": "Bearer test_student_hint"},
    )

    # Submit answer with assisted=False
    ans_res = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={
            "question_id": q_data["id"],
            "selected_option_key": "A",
            "confidence": "fairly_sure",
            "assisted": False,
        },
        headers={"Authorization": "Bearer test_student_hint"},
    )
    assert ans_res.status_code == 200

    # Verify server persisted assisted=True
    resp = db_session.query(Response).filter(Response.session_id == session_id).first()
    assert resp is not None
    assert resp.assisted is True


def test_early_submit_and_finalization(client: TestClient, db_session: Session):
    """POST /sessions/{id}/submit finalizes session and creates minimal snapshots (Section 11.5)."""
    create_res = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers={"Authorization": "Bearer test_student_submit"},
    )
    session_id = create_res.json()["session_id"]

    # Answer 1 question
    next_res = client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers={"Authorization": "Bearer test_student_submit"},
    )
    q_id = next_res.json()["question"]["id"]
    client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"question_id": q_id, "selected_option_key": "A", "confidence": "fairly_sure"},
        headers={"Authorization": "Bearer test_student_submit"},
    )

    # Submit session early
    submit_res = client.post(
        f"/api/v1/sessions/{session_id}/submit",
        headers={"Authorization": "Bearer test_student_submit"},
    )
    assert submit_res.status_code == 200
    sub_data = submit_res.json()
    assert sub_data["session_id"] == session_id
    assert sub_data["status"] == "completed"
    assert sub_data["completion_reason"] == "early_submit"
    assert sub_data["answered_count"] == 1

    # Verify diagnosis snapshots exist for all 8 concepts
    snapshots = (
        db_session.query(DiagnosisSnapshot)
        .filter(DiagnosisSnapshot.session_id == session_id)
        .all()
    )
    assert len(snapshots) == 8

    # Repeat submit is idempotent
    repeat_res = client.post(
        f"/api/v1/sessions/{session_id}/submit",
        headers={"Authorization": "Bearer test_student_submit"},
    )
    assert repeat_res.status_code == 200
    assert repeat_res.json()["status"] == "completed"


def test_cross_student_access_isolation(client: TestClient):
    """Student B cannot access Student A's session (returns 404) (Section 11.0, 11.13)."""
    # Student A creates session
    create_res = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers={"Authorization": "Bearer student_a"},
    )
    session_id = create_res.json()["session_id"]

    # Student B tries to access Student A's session
    cross_res = client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers={"Authorization": "Bearer student_b"},
    )
    assert cross_res.status_code == 404
    assert cross_res.json()["error"]["code"] == "SESSION_NOT_FOUND"
