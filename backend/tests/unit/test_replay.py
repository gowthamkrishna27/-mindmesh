"""Unit tests for deterministic replay service (Sections 7.5, 12, 14)."""

import pytest
from sqlalchemy.orm import Session
from app.models.curriculum import Concept, Question, QuestionOption
from app.models.engine import Response
from app.services.graph import GraphService
from app.services.replay import (
    replay_responses,
    replay_student_mastery_from_db,
)


@pytest.fixture
def test_graph():
    return GraphService(
        concept_ids=["D01", "D02", "D08", "D09"],
        edges=[("D01", "D02"), ("D02", "D08"), ("D08", "D09")],
    )


def test_replay_derives_epochs_and_mastery_identically(test_graph):
    student_id = "student_test_1"

    # Simulated questions map
    questions_map = {
        "Q1": {"id": "Q1", "primary_concept_id": "D01", "options": [{"option_key": "A", "is_correct": True}]},
        "Q2": {"id": "Q2", "primary_concept_id": "D01", "options": [{"option_key": "A", "is_correct": True}]},
        "Q3": {"id": "Q3", "primary_concept_id": "D01", "options": [{"option_key": "A", "is_correct": True}]},
        "Q4_retest": {"id": "Q4_retest", "primary_concept_id": "D01", "options": [{"option_key": "A", "is_correct": True}]},
        "Q5_retest": {"id": "Q5_retest", "primary_concept_id": "D01", "options": [{"option_key": "A", "is_correct": True}]},
    }

    # Responses:
    # 3 wrong answers in diagnostic session
    # followed by 2 correct answers in retest session
    responses = [
        {"question_id": "Q1", "session_id": "diag_session_1", "is_correct": False, "confidence": "fairly_sure", "attempt_number": 1},
        {"question_id": "Q2", "session_id": "diag_session_1", "is_correct": False, "confidence": "fairly_sure", "attempt_number": 1},
        {"question_id": "Q3", "session_id": "diag_session_1", "is_correct": False, "confidence": "fairly_sure", "attempt_number": 1},
        {"question_id": "Q4_retest", "session_id": "retest_session_1", "is_correct": True, "confidence": "fairly_sure", "attempt_number": 1},
        {"question_id": "Q5_retest", "session_id": "retest_session_1", "is_correct": True, "confidence": "fairly_sure", "attempt_number": 1},
    ]

    result = replay_responses(
        student_id=student_id,
        responses=responses,
        questions_map=questions_map,
        graph_service=test_graph,
        all_concept_ids=["D01", "D02", "D08", "D09"],
        retest_session_ids={"retest_session_1"},
    )

    # D01 should have 1 historical epoch (epoch 0) and current epoch 1
    assert len(result.epoch_histories["D01"]) == 1
    hist_0 = result.epoch_histories["D01"][0]
    assert hist_0.epoch_index == 0
    assert hist_0.final_status == "confirmed_gap"
    assert pytest.approx(hist_0.final_direct_estimate, 0.001) == 0.200

    # Current epoch 1 for D01
    curr_d01 = result.current_states["D01"]
    assert curr_d01.epoch_index == 1
    assert curr_d01.status == "mastered"
    assert pytest.approx(curr_d01.direct_estimate, 0.001) == 0.750
    assert curr_d01.ready is True

    # Retest outcome should be recovered
    outcome, limited = result.retest_outcomes["D01"]
    assert outcome == "recovered"
    assert limited is False

    # Trend should be improving (+0.55 >= 0.10)
    assert result.trends["D01"] == "improving"


def test_database_replay_roundtrip(db_session: Session):
    student_id = "student_replay_db"

def test_database_replay_roundtrip(db_session: Session):
    import os
    from app.db.seed import seed_curriculum

    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "app", "data"))
    seed_curriculum(db_session, data_dir=data_dir)

    student_id = "student_replay_db"

    # Add responses using seeded questions Q-D01-01 and Q-D01-02
    r1 = Response(
        student_id=student_id,
        session_id="diag_s1",
        question_id="Q-D01-01",
        selected_option_key="A",
        confidence="fairly_sure",
        is_correct=True,
        attempt_number=1,
        assisted=False,
        response_time_ms=25000,
        time_class="normal",
        option_changes=0,
        signals_incomplete=False,
        reason_tags=[],
    )
    r2 = Response(
        student_id=student_id,
        session_id="diag_s1",
        question_id="Q-D01-02",
        selected_option_key="A",
        confidence="fairly_sure",
        is_correct=True,
        attempt_number=1,
        assisted=False,
        response_time_ms=25000,
        time_class="normal",
        option_changes=0,
        signals_incomplete=False,
        reason_tags=[],
    )
    db_session.add_all([r1, r2])
    db_session.commit()

    replay_result = replay_student_mastery_from_db(db_session, student_id)
    assert replay_result.student_id == student_id
    d01_state = replay_result.current_states["D01"]
    assert d01_state.n_direct_questions == 2
    assert d01_state.n_direct_correct == 2
    assert pytest.approx(d01_state.direct_estimate, 0.001) == 0.750
    assert d01_state.status == "mastered"
    assert d01_state.ready is True

