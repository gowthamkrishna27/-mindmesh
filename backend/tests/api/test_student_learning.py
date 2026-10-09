"""API integration tests for student learning endpoints.

Conforms strictly to Specification v3.0 Sections 6, 7.5, 7.6, 9, 10, 11.6 - 11.12.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.seed import seed_curriculum
from app.models.curriculum import Concept, Question
from app.models.engine import Response, StudentConceptMastery
from app.models.session import DiagnosisSnapshot, LearningCompletion, Session as AssessmentSession, Student


@pytest.fixture(autouse=True)
def setup_curriculum(db_session: Session):
    """Seed curriculum data into test database."""
    seed_curriculum(db_session)


# --- 1. Diagnosis (Section 11.6) ---

def test_get_diagnosis_without_completed_session(client: TestClient):
    """GET /students/me/diagnosis returns empty/safe state if no completed diagnostic exists (Section 11.6)."""
    response = client.get(
        "/api/v1/students/me/diagnosis",
        headers={"Authorization": "Bearer student_no_test"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "student_no_test"
    assert data["session_id"] is None
    assert data["is_finalized"] is False
    assert data["root_gaps"] == []


def test_get_diagnosis_with_completed_session(client: TestClient, db_session: Session):
    """GET /students/me/diagnosis returns deterministic root gaps and learning path for completed session."""
    student_id = "student_diag_api"
    # Create and complete a diagnostic session
    sess = AssessmentSession(
        id="sess_diag_api_1",
        student_id=student_id,
        kind="diagnostic",
        status="completed",
        answered_count=3,
        question_limit=12,
        consent=True,
    )
    db_session.add(sess)

    # Set up mastery: D08 gap, D09 gap
    m_d08 = StudentConceptMastery(
        student_id=student_id,
        concept_id="D08",
        n_direct_questions=3,
        n_direct_incorrect=3,
        direct_estimate=0.20,
        mastery_estimate=0.20,
        status="confirmed_gap",
        ready=False,
    )
    m_d09 = StudentConceptMastery(
        student_id=student_id,
        concept_id="D09",
        n_direct_questions=1,
        n_direct_incorrect=1,
        direct_estimate=0.333,
        mastery_estimate=0.333,
        status="suspected_gap",
        ready=False,
    )
    db_session.add_all([m_d08, m_d09])
    db_session.commit()

    response = client.get(
        "/api/v1/students/me/diagnosis",
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_finalized"] is True
    assert data["session_id"] == "sess_diag_api_1"
    assert len(data["root_gaps"]) >= 1
    assert data["root_gaps"][0]["concept_id"] == "D08"
    assert len(data["learning_path"]) >= 2
    assert "rationale" in data


# --- 2. Learning Graph (Section 11.7) ---

def test_get_learning_graph(client: TestClient, db_session: Session):
    """GET /students/me/graph returns nodes with 4 visual states, readiness, and unlock status (Section 11.7)."""
    student_id = "student_graph_api"
    # D01 mastered, D02 mastered
    db_session.add_all([
        StudentConceptMastery(student_id=student_id, concept_id="D01", status="mastered", ready=True, direct_estimate=0.75),
        StudentConceptMastery(student_id=student_id, concept_id="D02", status="mastered", ready=True, direct_estimate=0.80),
        StudentConceptMastery(student_id=student_id, concept_id="D08", status="confirmed_gap", ready=False, direct_estimate=0.20),
    ])
    db_session.commit()

    response = client.get(
        "/api/v1/students/me/graph",
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 8  # 8 DBMS concepts

    nodes_by_id = {n["id"]: n for n in data["nodes"]}
    assert nodes_by_id["D01"]["visual_status"] == "mastered"
    assert nodes_by_id["D01"]["ready"] is True
    assert nodes_by_id["D08"]["visual_status"] == "needs_attention"
    assert nodes_by_id["D08"]["ready"] is False
    assert nodes_by_id["D13"]["visual_status"] == "unassessed"

    # D03 (Keys) depends on D02. Since D02 is ready, D03 is unlocked
    assert nodes_by_id["D03"]["unlocked"] is True


# --- 3. Concept Details (Section 11.8) ---

def test_get_concept_details(client: TestClient, db_session: Session):
    """GET /students/me/concepts/{id} returns details, resources at 3 depths, and attempt history (Section 11.8)."""
    student_id = "student_detail_api"
    db_session.add(StudentConceptMastery(
        student_id=student_id,
        concept_id="D08",
        status="confirmed_gap",
        ready=False,
        direct_estimate=0.25,
    ))
    db_session.commit()

    # Valid concept
    response = client.get(
        "/api/v1/students/me/concepts/D08",
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "D08"
    assert data["name"] == "SQL Basics"
    assert data["backend_status"] == "confirmed_gap"
    assert data["visual_status"] == "needs_attention"
    assert "resources" in data
    assert "quick_revision" in data["resources"]
    assert "standard" in data["resources"]
    assert "deep_learning" in data["resources"]
    assert "attempt_history" in data
    assert "suggested_depth" in data


def test_get_concept_details_unknown_concept(client: TestClient):
    """GET /students/me/concepts/{id} returns 404 for unknown concept ID."""
    response = client.get(
        "/api/v1/students/me/concepts/D99_UNKNOWN",
        headers={"Authorization": "Bearer student_detail_api"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CONCEPT_NOT_FOUND"


# --- 4. Post-Test Feedback (Section 11.9) ---

def test_feedback_disclosure_withheld_during_active_session(client: TestClient):
    """GET /students/me/feedback returns 409 while diagnostic is active (Section 11.9)."""
    student_id = "student_feed_active"
    # Create active session
    client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers={"Authorization": f"Bearer {student_id}"},
    )

    response = client.get(
        "/api/v1/students/me/feedback",
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DISCLOSURE_RESTRICTED"


def test_feedback_delivered_after_session_finalization(client: TestClient, db_session: Session):
    """GET /students/me/feedback returns detailed answers and explanations once completed (Section 11.9)."""
    student_id = "student_feed_done"
    create_res = client.post(
        "/api/v1/sessions",
        json={"kind": "diagnostic", "consent": True},
        headers={"Authorization": f"Bearer {student_id}"},
    )
    session_id = create_res.json()["session_id"]

    # Issue and answer 1 question
    next_res = client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers={"Authorization": f"Bearer {student_id}"},
    )
    q_data = next_res.json()["question"]
    client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"question_id": q_data["id"], "selected_option_key": "A", "confidence": "sure"},
        headers={"Authorization": f"Bearer {student_id}"},
    )

    # Submit session
    client.post(
        f"/api/v1/sessions/{session_id}/submit",
        headers={"Authorization": f"Bearer {student_id}"},
    )

    # Fetch feedback
    response = client.get(
        "/api/v1/students/me/feedback",
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert len(data["questions_feedback"]) == 1
    q_fb = data["questions_feedback"][0]
    assert q_fb["question_id"] == q_data["id"]
    assert "explanation" in q_fb
    assert "correct_option_key" in q_fb
    assert "is_correct" in q_fb


# --- 5. Progressive Hints (Section 11.10) ---

def test_hint_progression_order_enforced(client: TestClient, db_session: Session):
    """POST /concepts/{id}/hints enforces level 1 before level 2 progression (Section 11.10)."""
    student_id = "student_hints_order"
    q = db_session.query(Question).filter(Question.primary_concept_id == "D02").first()

    # Requesting level 2 directly must fail with 400
    res_lvl2_first = client.post(
        "/api/v1/students/me/concepts/D02/hints",
        json={"question_id": q.id, "requested_level": 2},
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert res_lvl2_first.status_code == 400
    assert res_lvl2_first.json()["error"]["code"] == "HINT_LEVEL_ORDER_VIOLATION"

    # Request level 1 first
    res_lvl1 = client.post(
        "/api/v1/students/me/concepts/D02/hints",
        json={"question_id": q.id, "requested_level": 1},
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert res_lvl1.status_code == 200
    assert res_lvl1.json()["hint_level"] == 1
    assert "content" in res_lvl1.json()

    # Now request level 2: must succeed
    res_lvl2 = client.post(
        "/api/v1/students/me/concepts/D02/hints",
        json={"question_id": q.id, "requested_level": 2},
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert res_lvl2.status_code == 200
    assert res_lvl2.json()["hint_level"] == 2


def test_hint_does_not_modify_mastery_or_reveal_answers(client: TestClient, db_session: Session):
    """Hints never leak the answer key or modify mastery (Section 11.10)."""
    student_id = "student_hint_safe"
    q = db_session.query(Question).filter(Question.primary_concept_id == "D02").first()

    res = client.post(
        "/api/v1/students/me/concepts/D02/hints",
        json={"question_id": q.id, "requested_level": 1},
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert res.status_code == 200
    hint_data = res.json()
    assert "correct_option_id" not in hint_data
    assert "correct_option_key" not in hint_data

    # Mastery should remain unassessed
    m = db_session.query(StudentConceptMastery).filter(
        StudentConceptMastery.student_id == student_id,
        StudentConceptMastery.concept_id == "D02",
    ).first()
    assert m is None or m.status == "unassessed"


# --- 6. Learning Completion (Section 11.11) ---

def test_learning_completion_idempotent_and_no_premature_mastery(client: TestClient, db_session: Session):
    """POST /learning/{id}/complete enables retest without altering mastery or epochs (Section 6.2, 11.11)."""
    student_id = "student_learn_comp"

    # First completion call
    res1 = client.post(
        "/api/v1/students/me/learning/D08/complete",
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "completed"
    assert data1["concept_id"] == "D08"
    assert data1["retest_enabled"] is True

    # Repeated completion call is idempotent
    res2 = client.post(
        "/api/v1/students/me/learning/D08/complete",
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "completed"

    # CRITICAL: Verify mastery was NOT granted or updated
    m = db_session.query(StudentConceptMastery).filter(
        StudentConceptMastery.student_id == student_id,
        StudentConceptMastery.concept_id == "D08",
    ).first()
    assert m is None or m.status != "mastered"


# --- 7. Historical Report (Section 11.12) ---

def test_historical_report_epoch_analysis(client: TestClient, db_session: Session):
    """GET /students/me/report compares before-and-after epoch snapshots with retest outcomes (Section 11.12)."""
    student_id = "student_report_api"

    response = client.get(
        "/api/v1/students/me/report",
        headers={"Authorization": f"Bearer {student_id}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == student_id
    assert len(data["concepts"]) == 8

    # Each concept report has epoch comparison metrics
    for cr in data["concepts"]:
        assert "concept_id" in cr
        assert "current_status" in cr
        assert "outcome" in cr
        assert "verification_limited" in cr
        assert "ready" in cr
        assert "trend" in cr
        assert "epochs" in cr
