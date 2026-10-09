"""Unit tests for adaptive question selection engine.

Conforms strictly to Specification v3.0 Sections 5.3, 8.1 - 8.3.
"""

import pytest
from sqlalchemy.orm import Session
from app.db.seed import seed_curriculum
from app.models.curriculum import Concept, Question
from app.models.engine import Response, StudentConceptMastery
from app.models.session import SelectionLog, Session as AssessmentSession, SessionQuestionIssue, Student
from app.services.graph import load_graph_from_db
from app.services.question_selector import QuestionSelector, BASELINE_CONCEPT_ORDER


@pytest.fixture
def seeded_db(db_session: Session) -> Session:
    """Fixture with seeded curriculum and graph."""
    seed_curriculum(db_session)
    return db_session


@pytest.fixture
def test_student(seeded_db: Session) -> Student:
    """Fixture creating a test student."""
    student = Student(id="student_sel_test", name="Selector Test Student", consent_given=True)
    seeded_db.add(student)
    seeded_db.commit()
    return student


@pytest.fixture
def diagnostic_session(seeded_db: Session, test_student: Student) -> AssessmentSession:
    """Fixture creating an active diagnostic assessment session."""
    sess = AssessmentSession(
        id="sess_sel_diag",
        student_id=test_student.id,
        kind="diagnostic",
        status="active",
        question_limit=12,
        answered_count=0,
        consent=True,
    )
    seeded_db.add(sess)
    seeded_db.commit()
    return sess


def test_baseline_selection_sequence(seeded_db: Session, diagnostic_session: AssessmentSession):
    """Test that baseline phase issues questions in order: D02, D03, D08, D01 (Section 8.1)."""
    graph = load_graph_from_db(seeded_db)
    selector = QuestionSelector(seeded_db, graph)

    expected_baseline = ["D02", "D03", "D08", "D01"]
    for expected_cid in expected_baseline:
        result = selector.select_next_diagnostic_question(
            session_id=diagnostic_session.id,
            student_id=diagnostic_session.student_id,
        )
        assert result.question is not None
        assert result.question.primary_concept_id == expected_cid
        assert result.reason == f"baseline_coverage:{expected_cid}"

        # Record issue so selector knows this question has been issued
        issue = SessionQuestionIssue(
            session_id=diagnostic_session.id,
            question_id=result.question.id,
            status="issued",
        )
        seeded_db.add(issue)
        seeded_db.commit()


def test_held_out_retest_items_reserved(seeded_db: Session, diagnostic_session: AssessmentSession):
    """Test that held-out retest items (use_for_retest=True) are not selected during diagnosis (Section 5.3, 8.2)."""
    graph = load_graph_from_db(seeded_db)
    selector = QuestionSelector(seeded_db, graph)

    # In seed data, each concept has 3 diagnostic and 2 retest items
    # Baseline selects D02
    result = selector.select_next_diagnostic_question(
        session_id=diagnostic_session.id,
        student_id=diagnostic_session.student_id,
    )
    assert result.question is not None
    assert result.question.primary_concept_id == "D02"
    assert result.question.use_for_retest is False
    assert result.question.use_for_diagnosis is True


def test_per_concept_diagnostic_cap(seeded_db: Session, diagnostic_session: AssessmentSession):
    """Test that at most 3 questions are issued per concept in a diagnostic session (Section 5.3, 8.2)."""
    graph = load_graph_from_db(seeded_db)
    selector = QuestionSelector(seeded_db, graph)

    # Issue 3 questions for D02
    d02_qs = seeded_db.query(Question).filter(Question.primary_concept_id == "D02").limit(3).all()
    for q in d02_qs:
        issue = SessionQuestionIssue(
            session_id=diagnostic_session.id,
            question_id=q.id,
            status="issued",
        )
        seeded_db.add(issue)
    seeded_db.commit()

    # D02 has reached the 3-question cap; baseline should skip D02 and select D03
    result = selector.select_next_diagnostic_question(
        session_id=diagnostic_session.id,
        student_id=diagnostic_session.student_id,
    )
    assert result.question is not None
    assert result.question.primary_concept_id == "D03"


def test_prerequisite_probe_on_failed_concept(seeded_db: Session, diagnostic_session: AssessmentSession):
    """Test prerequisite probe triggers on most recently failed concept T for direct unasked prereq P (Section 8.1)."""
    graph = load_graph_from_db(seeded_db)
    selector = QuestionSelector(seeded_db, graph)

    # Mark baseline questions as issued to pass baseline phase:
    # Baseline needs D02, D03, D08, D01 issued
    for cid in BASELINE_CONCEPT_ORDER:
        q = seeded_db.query(Question).filter(Question.primary_concept_id == cid).first()
        issue = SessionQuestionIssue(session_id=diagnostic_session.id, question_id=q.id, status="answered")
        seeded_db.add(issue)
    seeded_db.commit()

    # Suppose student answered a question on D04 (Integrity Constraints) and failed:
    # Prerequisites of D04 are D02 and D03.
    # D02 and D03 were already asked in baseline.
    # What if a question on D13 (Normalization) failed?
    # Direct prerequisites of D13 are D12 (Functional Dependencies) and D03 (Keys).
    # D12 was NOT asked yet! D03 was asked in baseline.
    q_d13 = seeded_db.query(Question).filter(Question.primary_concept_id == "D13").first()
    issue_d13 = SessionQuestionIssue(session_id=diagnostic_session.id, question_id=q_d13.id, status="answered")
    seeded_db.add(issue_d13)

    # Add a failed response for D13
    resp_d13 = Response(
        student_id=diagnostic_session.student_id,
        session_id=diagnostic_session.id,
        question_id=q_d13.id,
        selected_option_key="B",
        confidence="sure",
        is_correct=False,
        response_time_ms=5000,
        time_class="normal",
    )
    seeded_db.add(resp_d13)

    # Create failed mastery state for D13 (n_direct_incorrect >= 1, direct_estimate < 0.50)
    mastery_d13 = StudentConceptMastery(
        student_id=diagnostic_session.student_id,
        concept_id="D13",
        n_direct_questions=1,
        n_direct_incorrect=1,
        direct_estimate=0.333,
        mastery_estimate=0.333,
        status="suspected_gap",
    )
    seeded_db.add(mastery_d13)
    seeded_db.commit()

    # Next question selection should trigger prerequisite probe on D12 (direct prereq of D13 with no direct question yet)
    result = selector.select_next_diagnostic_question(
        session_id=diagnostic_session.id,
        student_id=diagnostic_session.student_id,
    )
    assert result.question is not None
    assert result.question.primary_concept_id == "D12"
    assert result.reason == "prerequisite_probe:T=D13,P=D12"


def test_prerequisite_probe_at_most_once_per_pair(seeded_db: Session, diagnostic_session: AssessmentSession):
    """Test that at most one prerequisite probe fires per (T, P) pair (Section 8.1)."""
    graph = load_graph_from_db(seeded_db)
    selector = QuestionSelector(seeded_db, graph)

    # Mark baseline questions as issued
    for cid in BASELINE_CONCEPT_ORDER:
        q = seeded_db.query(Question).filter(Question.primary_concept_id == cid).first()
        seeded_db.add(SessionQuestionIssue(session_id=diagnostic_session.id, question_id=q.id, status="answered"))

    # Fail D13
    q_d13 = seeded_db.query(Question).filter(Question.primary_concept_id == "D13").first()
    seeded_db.add(SessionQuestionIssue(session_id=diagnostic_session.id, question_id=q_d13.id, status="answered"))
    seeded_db.add(Response(
        student_id=diagnostic_session.student_id,
        session_id=diagnostic_session.id,
        question_id=q_d13.id,
        selected_option_key="B",
        confidence="sure",
        is_correct=False,
        response_time_ms=5000,
        time_class="normal",
    ))
    seeded_db.add(StudentConceptMastery(
        student_id=diagnostic_session.student_id,
        concept_id="D13",
        n_direct_questions=1,
        n_direct_incorrect=1,
        direct_estimate=0.333,
        mastery_estimate=0.333,
        status="suspected_gap",
    ))

    # Record that (D13, D12) was already probed
    seeded_db.add(SelectionLog(
        session_id=diagnostic_session.id,
        question_id="Q-D12-01",
        reason="prerequisite_probe:T=D13,P=D12",
        candidate_scores={},
    ))
    seeded_db.commit()

    # Now that (D13, D12) has been probed, selector should NOT probe (D13, D12) again
    result = selector.select_next_diagnostic_question(
        session_id=diagnostic_session.id,
        student_id=diagnostic_session.student_id,
    )
    assert result.question is not None
    assert result.reason != "prerequisite_probe:T=D13,P=D12"
    assert result.reason == "ranked_selection"


def test_session_limit_reached(seeded_db: Session, diagnostic_session: AssessmentSession):
    """Test that selector stops when 12 questions have been issued (Section 8.1, 8.2)."""
    graph = load_graph_from_db(seeded_db)
    selector = QuestionSelector(seeded_db, graph)

    all_qs = seeded_db.query(Question).limit(12).all()
    for q in all_qs:
        seeded_db.add(SessionQuestionIssue(
            session_id=diagnostic_session.id,
            question_id=q.id,
            status="issued",
        ))
    seeded_db.commit()

    result = selector.select_next_diagnostic_question(
        session_id=diagnostic_session.id,
        student_id=diagnostic_session.student_id,
    )
    assert result.question is None
    assert result.exhausted is True
    assert result.reason == "session_limit_reached"


def test_ranked_selection_scores(seeded_db: Session, diagnostic_session: AssessmentSession):
    """Test ranked selection candidate score computation and audit persistence (Section 8.3)."""
    graph = load_graph_from_db(seeded_db)
    selector = QuestionSelector(seeded_db, graph)

    # Issue baseline questions
    for cid in BASELINE_CONCEPT_ORDER:
        q = seeded_db.query(Question).filter(Question.primary_concept_id == cid).first()
        seeded_db.add(SessionQuestionIssue(session_id=diagnostic_session.id, question_id=q.id, status="answered"))
    seeded_db.commit()

    result = selector.select_next_diagnostic_question(
        session_id=diagnostic_session.id,
        student_id=diagnostic_session.student_id,
    )
    assert result.question is not None
    assert result.reason == "ranked_selection"
    assert len(result.candidate_scores) > 0

    # Verify score components for candidates
    for cid, scores in result.candidate_scores.items():
        assert "U" in scores
        assert "I" in scores
        assert "S" in scores
        assert "C" in scores
        assert "rank_score" in scores
        # Verify rank_score formula: 0.40*U + 0.25*I + 0.25*S + 0.10*C
        expected = round(0.40 * scores["U"] + 0.25 * scores["I"] + 0.25 * scores["S"] + 0.10 * scores["C"], 4)
        assert abs(scores["rank_score"] - expected) <= 0.001

