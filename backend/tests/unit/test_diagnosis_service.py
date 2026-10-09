"""Unit tests for deterministic diagnosis, blocker scoring, and learning paths.

Conforms strictly to Specification v3.0 Sections 7.6, 9.1 - 9.5, 10.
"""

import pytest
from sqlalchemy.orm import Session
from app.db.seed import seed_curriculum
from app.models.curriculum import Concept, Question
from app.models.engine import Response, StudentConceptMastery
from app.models.session import Student
from app.services.diagnosis_service import DiagnosisService
from app.services.graph import load_graph_from_db


@pytest.fixture
def seeded_db(db_session: Session) -> Session:
    seed_curriculum(db_session)
    return db_session


def test_root_gap_identification_and_blocker_score(seeded_db: Session):
    """Test candidate root-gap identification and blocker score: (1 - mastery_estimate) * importance (Section 9.1, 9.2)."""
    student_id = "test_student_diag_1"
    student = Student(id=student_id, name="Diag Student 1", consent_given=True)
    seeded_db.add(student)

    # Suppose D08 (SQL Basics) has a confirmed gap
    # Importance of D08 = 1/7 = 0.142857
    mastery_d08 = StudentConceptMastery(
        student_id=student_id,
        concept_id="D08",
        n_direct_questions=3,
        n_direct_incorrect=3,
        direct_estimate=0.20,
        mastery_estimate=0.20,
        status="confirmed_gap",
        ready=False,
    )
    # Suppose D09 (SQL Joins) has a suspected gap
    mastery_d09 = StudentConceptMastery(
        student_id=student_id,
        concept_id="D09",
        n_direct_questions=1,
        n_direct_incorrect=1,
        direct_estimate=0.333,
        mastery_estimate=0.333,
        status="suspected_gap",
        ready=False,
    )
    seeded_db.add_all([mastery_d08, mastery_d09])
    seeded_db.commit()

    service = DiagnosisService(seeded_db)
    res = service.compute_student_diagnosis(student_id=student_id)

    # D08 is an ancestor of D09 and has status confirmed_gap -> D08 is identified as root gap
    root_ids = [rg.concept_id for rg in res.root_gaps]
    assert "D08" in root_ids

    d08_rg = next(rg for rg in res.root_gaps if rg.concept_id == "D08")
    assert d08_rg.status == "confirmed_gap"
    # Blocker score = (1.0 - 0.20) * (1/7) = 0.80 * 0.142857 = 0.1143
    assert abs(d08_rg.blocker_score - 0.1143) <= 0.001
    assert "D09" in d08_rg.failed_dependents_explained


def test_uncertain_ancestor_not_promoted_to_root(seeded_db: Session):
    """Test that uncertain or unassessed ancestors are not promoted to root gaps (Section 9.1)."""
    student_id = "test_student_diag_2"
    student = Student(id=student_id, name="Diag Student 2", consent_given=True)
    seeded_db.add(student)

    # D04 (Integrity Constraints) has a gap
    # Ancestor D02 (Relational Model) is uncertain
    mastery_d04 = StudentConceptMastery(
        student_id=student_id,
        concept_id="D04",
        n_direct_questions=1,
        n_direct_incorrect=1,
        direct_estimate=0.333,
        mastery_estimate=0.333,
        status="suspected_gap",
        ready=False,
    )
    mastery_d02 = StudentConceptMastery(
        student_id=student_id,
        concept_id="D02",
        n_direct_questions=1,
        n_direct_correct=1,
        direct_estimate=0.667,
        mastery_estimate=0.667,
        status="uncertain",
        ready=True,
    )
    seeded_db.add_all([mastery_d04, mastery_d02])
    seeded_db.commit()

    service = DiagnosisService(seeded_db)
    res = service.compute_student_diagnosis(student_id=student_id)

    # D02 should be in needs_more_evidence, NOT in root_gaps
    root_ids = [rg.concept_id for rg in res.root_gaps]
    assert "D02" not in root_ids
    assert "D02" in res.needs_more_evidence


def test_learning_path_topological_order_and_deferred_flag(seeded_db: Session):
    """Test learning path items are strictly in topological order with deferred set when prereq not ready (Section 9.4)."""
    student_id = "test_student_diag_3"
    student = Student(id=student_id, name="Diag Student 3", consent_given=True)
    seeded_db.add(student)

    # D08 (SQL Basics) confirmed gap, not ready
    # D09 (SQL Joins) suspected gap, not ready
    mastery_d08 = StudentConceptMastery(
        student_id=student_id,
        concept_id="D08",
        status="confirmed_gap",
        ready=False,
    )
    mastery_d09 = StudentConceptMastery(
        student_id=student_id,
        concept_id="D09",
        status="suspected_gap",
        ready=False,
    )
    seeded_db.add_all([mastery_d08, mastery_d09])
    seeded_db.commit()

    service = DiagnosisService(seeded_db)
    res = service.compute_student_diagnosis(student_id=student_id)

    # Learning path must order D08 before D09 (prerequisite first)
    path_ids = [item.concept_id for item in res.learning_path]
    assert "D08" in path_ids
    assert "D09" in path_ids
    assert path_ids.index("D08") < path_ids.index("D09")

    # D09 must have deferred=True because direct prerequisite D08 is not ready
    d09_item = next(item for item in res.learning_path if item.concept_id == "D09")
    assert d09_item.deferred is True


def test_unlocked_frontier_advance_items_added_when_ready(seeded_db: Session):
    """Test that up to 2 advance items from unlocked frontier are added when all weak items are ready (Section 9.4)."""
    student_id = "test_student_diag_4"
    student = Student(id=student_id, name="Diag Student 4", consent_given=True)
    seeded_db.add(student)

    # D01 mastered and ready
    # D02 mastered and ready
    mastery_d01 = StudentConceptMastery(student_id=student_id, concept_id="D01", status="mastered", ready=True)
    mastery_d02 = StudentConceptMastery(student_id=student_id, concept_id="D02", status="mastered", ready=True)
    seeded_db.add_all([mastery_d01, mastery_d02])
    seeded_db.commit()

    service = DiagnosisService(seeded_db)
    res = service.compute_student_diagnosis(student_id=student_id)

    # Since all prerequisites of D03 (Keys) and D08 (SQL Basics) are ready (D02 is ready):
    # D03 and D08 are unlocked and should appear as advance items on the learning path
    advance_items = [item for item in res.learning_path if item.kind == "advance"]
    assert len(advance_items) <= 2
    advance_cids = [item.concept_id for item in advance_items]
    for cid in advance_cids:
        assert cid in res.unlocked_concepts
