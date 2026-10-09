"""End-to-End Integrity, Idempotency, Atomic Rollback, and Deterministic Replay Journey.

Conforms to Specification v3.0 Sections 7, 11.4, 11.5, 12, 13, 14.
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.seed import seed_curriculum
from app.models.engine import Response, ResponseEvidence, StudentConceptMastery
from app.models.session import DiagnosisSnapshot
from app.services.replay import replay_student_mastery_from_db


def test_integrity_and_recovery_journey(client: TestClient, db_session: Session):
    """Verify atomic answer persistence, duplicate prevention, transaction rollback, replay consistency, and snapshot immutability."""
    # 1. Seed curriculum
    seed_curriculum(db_session)
    student_headers = {"X-Student-Id": "integrity_student_1"}

    # 2. Create diagnostic session
    res_sess = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers=student_headers,
    )
    assert res_sess.status_code == 201
    session_id = res_sess.json()["session_id"]

    # 3. Issue question
    res_next = client.get(f"/api/v1/sessions/{session_id}/next", headers=student_headers)
    assert res_next.status_code == 200
    q_data = res_next.json()["question"]
    q_id = q_data["id"]
    opt_id = q_data["options"][0]["id"]

    # 4. Step 1: Submit answer and verify Response, Evidence, and Mastery update atomically
    res_submit = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"question_id": q_id, "selected_option_id": opt_id, "confidence": "sure"},
        headers=student_headers,
    )
    assert res_submit.status_code == 200

    resp_row = db_session.query(Response).filter(Response.session_id == session_id, Response.question_id == q_id).first()
    assert resp_row is not None
    initial_resp_id = resp_row.id

    evidence_count = db_session.query(ResponseEvidence).filter(ResponseEvidence.response_id == initial_resp_id).count()
    assert evidence_count >= 1

    mastery_rows = db_session.query(StudentConceptMastery).filter(StudentConceptMastery.student_id == "integrity_student_1").all()
    assert len(mastery_rows) >= 1

    # 5. Step 2: Retry the submission -> must be rejected with 409 Conflict, without duplicating evidence
    res_retry = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"question_id": q_id, "selected_option_id": opt_id, "confidence": "sure"},
        headers=student_headers,
    )
    assert res_retry.status_code == 409
    assert res_retry.json()["error"]["code"] == "DUPLICATE_ANSWER"

    evidence_count_after = db_session.query(ResponseEvidence).filter(ResponseEvidence.response_id == initial_resp_id).count()
    assert evidence_count_after == evidence_count  # No duplicate evidence created

    # 6. Step 3: Simulate persistence failure and verify transaction rollback
    # Issue next question
    res_next2 = client.get(f"/api/v1/sessions/{session_id}/next", headers=student_headers)
    q2_id = res_next2.json()["question"]["id"]
    q2_opt_id = res_next2.json()["question"]["options"][0]["id"]

    # Simulate an error during evidence application / flush
    with patch("app.services.session_service.apply_evidence_item", side_effect=RuntimeError("Simulated database failure")):
        try:
            client.post(
                f"/api/v1/sessions/{session_id}/answers",
                json={"question_id": q2_id, "selected_option_id": q2_opt_id, "confidence": "sure"},
                headers=student_headers,
            )
        except RuntimeError:
            pass

    # Verify no orphan response was created for q2
    orphan_resp = db_session.query(Response).filter(Response.session_id == session_id, Response.question_id == q2_id).first()
    assert orphan_resp is None

    # 7. Step 4: Replay persisted evidence and verify derived state matches
    replay_result = replay_student_mastery_from_db(db_session, "integrity_student_1")
    assert replay_result.student_id == "integrity_student_1"
    for cid, state in replay_result.current_states.items():
        db_m = db_session.query(StudentConceptMastery).filter(
            StudentConceptMastery.student_id == "integrity_student_1",
            StudentConceptMastery.concept_id == cid,
        ).first()
        if db_m:
            assert abs(state.mastery_estimate - db_m.mastery_estimate) < 1e-4
            assert abs(state.direct_estimate - db_m.direct_estimate) < 1e-4
            assert state.status == db_m.status

    # 8. Step 5: Verify historical diagnosis snapshot immutability
    # Finalize session to create snapshot
    client.post(f"/api/v1/sessions/{session_id}/submit", headers=student_headers)
    initial_snapshots = (
        db_session.query(DiagnosisSnapshot)
        .filter(DiagnosisSnapshot.session_id == session_id)
        .all()
    )
    initial_estimates = {s.concept_id: (s.mastery_estimate, s.status) for s in initial_snapshots}

    # Perform another activity (learning complete on D01)
    client.post("/api/v1/students/me/learning/D01/complete", headers=student_headers)

    # Re-query initial snapshots: must be completely unchanged
    db_session.expire_all()
    snapshots_after = (
        db_session.query(DiagnosisSnapshot)
        .filter(DiagnosisSnapshot.session_id == session_id)
        .all()
    )
    for s in snapshots_after:
        prev_est, prev_status = initial_estimates[s.concept_id]
        assert s.mastery_estimate == prev_est
        assert s.status == prev_status
