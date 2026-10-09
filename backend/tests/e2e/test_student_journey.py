"""End-to-End Student Assessment and Adaptive Learning Journey.

Conforms to Specification v3.0 Sections 6, 7, 8, 9, 10, 11, 14.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.seed import seed_curriculum


def test_complete_student_learning_journey(client: TestClient, db_session: Session):
    """Verify complete student diagnostic, diagnosis, feedback, learning completion, and retest journey."""
    # 1. Seed curriculum
    seed_curriculum(db_session)

    # 2. Authenticate as a new student
    student_headers = {"X-Student-Id": "journey_student_1"}

    # 3. Create diagnostic session with consent
    res_sess = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers=student_headers,
    )
    assert res_sess.status_code == 201
    sess_data = res_sess.json()
    session_id = sess_data["session_id"]
    assert sess_data["status"] == "active"
    assert sess_data["question_limit"] == 12

    # 4. Answer diagnostic questions iteratively until finalized
    answered = 0
    while answered < 12:
        # Fetch next question idempotently
        res_next = client.get(f"/api/v1/sessions/{session_id}/next", headers=student_headers)
        assert res_next.status_code == 200
        next_data = res_next.json()
        if not next_data.get("question") or next_data.get("status") == "finalized":
            break

        question = next_data["question"]
        q_id = question["id"]
        options = question["options"]

        # Record interaction event
        res_ev = client.post(
            f"/api/v1/sessions/{session_id}/events",
            json={
                "event_type": "option_changed",
                "question_id": q_id,
                "payload": {"from_option_id": None, "to_option_id": options[0]["id"]},
            },
            headers=student_headers,
        )
        assert res_ev.status_code == 200

        # Submit answer (choose first option)
        res_ans = client.post(
            f"/api/v1/sessions/{session_id}/answers",
            json={
                "question_id": q_id,
                "selected_option_id": options[0]["id"],
                "confidence": "sure",
            },
            headers=student_headers,
        )
        assert res_ans.status_code == 200
        ans_data = res_ans.json()
        answered = ans_data["progress"]["answered_count"]
        if ans_data["session_completed"]:
            break

    # Finalize if not already complete
    res_submit = client.post(f"/api/v1/sessions/{session_id}/submit", headers=student_headers)
    assert res_submit.status_code == 200
    assert res_submit.json()["status"] == "completed"

    # 5. Retrieve student diagnosis, graph, and concept detail
    res_diag = client.get("/api/v1/students/me/diagnosis", headers=student_headers)
    assert res_diag.status_code == 200
    diag_data = res_diag.json()
    assert diag_data["is_finalized"] is True
    assert diag_data["session_id"] == session_id

    res_graph = client.get("/api/v1/students/me/graph", headers=student_headers)
    assert res_graph.status_code == 200
    assert len(res_graph.json()["nodes"]) == 8

    # Inspect first concept
    first_cid = diag_data["learning_path"][0]["concept_id"] if diag_data["learning_path"] else "D01"
    res_concept = client.get(f"/api/v1/students/me/concepts/{first_cid}", headers=student_headers)
    assert res_concept.status_code == 200
    concept_detail = res_concept.json()
    assert concept_detail["id"] == first_cid
    assert "resources" in concept_detail

    # 6. Retrieve post-test feedback
    res_feedback = client.get("/api/v1/students/me/feedback", headers=student_headers)
    assert res_feedback.status_code == 200
    feedback_data = res_feedback.json()
    assert feedback_data["session_id"] == session_id
    assert len(feedback_data["questions_feedback"]) >= 1

    # 7. Complete learning on concept
    res_learn = client.post(f"/api/v1/students/me/learning/{first_cid}/complete", headers=student_headers)
    assert res_learn.status_code == 200
    assert res_learn.json()["retest_enabled"] is True

    # Check that learning completion did NOT open a new epoch or alter mastery prematurely
    res_concept_after = client.get(f"/api/v1/students/me/concepts/{first_cid}", headers=student_headers)
    assert res_concept_after.json()["estimate"] == concept_detail["estimate"]

    # 8. Start and complete a retest session
    res_retest = client.post(
        "/api/v1/sessions",
        json={"kind": "retest", "consent": True},
        headers=student_headers,
    )
    assert res_retest.status_code == 201
    retest_sess_id = res_retest.json()["session_id"]

    # Fetch retest question
    res_retest_next = client.get(f"/api/v1/sessions/{retest_sess_id}/next", headers=student_headers)
    assert res_retest_next.status_code == 200
    rq = res_retest_next.json().get("question")
    if rq:
        # Answer held-out retest question
        client.post(
            f"/api/v1/sessions/{retest_sess_id}/answers",
            json={
                "question_id": rq["id"],
                "selected_option_id": rq["options"][0]["id"],
                "confidence": "sure",
            },
            headers=student_headers,
        )

    # Finalize retest
    client.post(f"/api/v1/sessions/{retest_sess_id}/submit", headers=student_headers)

    # 9. Verify historical report with epoch tracking
    res_report = client.get("/api/v1/students/me/report", headers=student_headers)
    assert res_report.status_code == 200
    report_data = res_report.json()
    assert report_data["student_id"] == "journey_student_1"
    assert len(report_data["concepts"]) == 8

    # Concept reports have outcome labels and epoch history
    for cr in report_data["concepts"]:
        assert cr["outcome"] in ("recovered", "improving", "no_change", "declined", "not_verified")
        assert len(cr["epochs"]) >= 1
