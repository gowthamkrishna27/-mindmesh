"""Unit tests for evidence epochs, retest outcomes, trends, and likely causes (Sections 7.5, 7.6, 7.7)."""

import pytest
from app.services.evidence import GeneratedEvidenceItem
from app.services.mastery import (
    ConceptMasteryState,
    apply_evidence_item,
    calculate_persistent_gap,
    calculate_retest_outcome,
    calculate_trend,
    determine_likely_cause,
)


def test_retest_hand_checked_examples_table():
    """Verify all 7 hand-checked examples from Section 7.5 table.

    Previous epoch ended in 'confirmed_gap' (estimate 0.200, rank 3).
    """
    prev_status = "confirmed_gap"

    # Row 1: none
    outcome, limited = calculate_retest_outcome(
        prev_status=prev_status,
        current_status="confirmed_gap",
        fresh_direct_count=0,
        fresh_correct_count=0,
        fresh_unassisted_count=0,
    )
    assert outcome == "not_verified"
    assert limited is True

    # Row 2: right (w=1) -> est 0.667, uncertain, ready yes
    state_r1 = ConceptMasteryState(concept_id="TEST", epoch_index=1)
    apply_evidence_item(state_r1, GeneratedEvidenceItem("TEST", "primary_direct", "positive", 1.0))
    assert pytest.approx(state_r1.direct_estimate, 0.001) == 0.667
    assert state_r1.status == "uncertain"
    assert state_r1.ready is True
    outcome, limited = calculate_retest_outcome(
        prev_status=prev_status,
        current_status=state_r1.status,
        fresh_direct_count=1,
        fresh_correct_count=1,
        fresh_unassisted_count=1,
    )
    assert outcome == "improving"
    assert limited is True

    # Row 3: right (not_sure, 0.6) -> est 0.615, uncertain, ready yes
    state_r_ns = ConceptMasteryState(concept_id="TEST", epoch_index=1)
    apply_evidence_item(state_r_ns, GeneratedEvidenceItem("TEST", "primary_direct", "positive", 0.6))
    assert pytest.approx(state_r_ns.direct_estimate, 0.001) == 0.615
    assert state_r_ns.status == "uncertain"
    assert state_r_ns.ready is True
    outcome, limited = calculate_retest_outcome(
        prev_status=prev_status,
        current_status=state_r_ns.status,
        fresh_direct_count=1,
        fresh_correct_count=1,
        fresh_unassisted_count=1,
    )
    assert outcome == "improving"
    assert limited is True

    # Row 4: right, right (w=1 each) -> est 0.750, mastered, ready yes
    state_r2 = ConceptMasteryState(concept_id="TEST", epoch_index=1)
    apply_evidence_item(state_r2, GeneratedEvidenceItem("TEST", "primary_direct", "positive", 1.0))
    apply_evidence_item(state_r2, GeneratedEvidenceItem("TEST", "primary_direct", "positive", 1.0))
    assert pytest.approx(state_r2.direct_estimate, 0.001) == 0.750
    assert state_r2.status == "mastered"
    assert state_r2.ready is True
    outcome, limited = calculate_retest_outcome(
        prev_status=prev_status,
        current_status=state_r2.status,
        fresh_direct_count=2,
        fresh_correct_count=2,
        fresh_unassisted_count=2,
    )
    assert outcome == "recovered"
    assert limited is False

    # Row 5: right, wrong (w=1 each) -> est 0.500, uncertain, ready no
    state_rw = ConceptMasteryState(concept_id="TEST", epoch_index=1)
    apply_evidence_item(state_rw, GeneratedEvidenceItem("TEST", "primary_direct", "positive", 1.0))
    apply_evidence_item(state_rw, GeneratedEvidenceItem("TEST", "primary_direct", "negative", 1.0))
    assert pytest.approx(state_rw.direct_estimate, 0.001) == 0.500
    assert state_rw.status == "uncertain"
    assert state_rw.ready is False
    outcome, limited = calculate_retest_outcome(
        prev_status=prev_status,
        current_status=state_rw.status,
        fresh_direct_count=2,
        fresh_correct_count=1,
        fresh_unassisted_count=2,
    )
    assert outcome == "improving"
    assert limited is False

    # Row 6: wrong (w=1) -> est 0.333, suspected_gap, ready no
    state_w1 = ConceptMasteryState(concept_id="TEST", epoch_index=1)
    apply_evidence_item(state_w1, GeneratedEvidenceItem("TEST", "primary_direct", "negative", 1.0))
    assert pytest.approx(state_w1.direct_estimate, 0.001) == 0.333
    assert state_w1.status == "suspected_gap"
    assert state_w1.ready is False
    outcome, limited = calculate_retest_outcome(
        prev_status=prev_status,
        current_status=state_w1.status,
        fresh_direct_count=1,
        fresh_correct_count=0,
        fresh_unassisted_count=1,
    )
    assert outcome == "no_change"
    assert limited is True

    # Row 7: wrong, wrong (w=1 each) -> est 0.250, suspected_gap, ready no
    state_w2 = ConceptMasteryState(concept_id="TEST", epoch_index=1)
    apply_evidence_item(state_w2, GeneratedEvidenceItem("TEST", "primary_direct", "negative", 1.0))
    apply_evidence_item(state_w2, GeneratedEvidenceItem("TEST", "primary_direct", "negative", 1.0))
    assert pytest.approx(state_w2.direct_estimate, 0.001) == 0.250
    assert state_w2.status == "suspected_gap"
    assert state_w2.ready is False
    outcome, limited = calculate_retest_outcome(
        prev_status=prev_status,
        current_status=state_w2.status,
        fresh_direct_count=2,
        fresh_correct_count=0,
        fresh_unassisted_count=2,
    )
    assert outcome == "no_change"
    assert limited is False


def test_calculate_trend():
    assert calculate_trend([0.5]) == "none"
    assert calculate_trend([0.20, 0.35]) == "improving"  # +0.15 >= 0.10
    assert calculate_trend([0.60, 0.45]) == "declining"  # -0.15 <= -0.10
    assert calculate_trend([0.50, 0.55]) == "flat"       # +0.05 < 0.10


def test_calculate_persistent_gap():
    # Past gap + current gap + at least 1 answer -> True
    assert calculate_persistent_gap(
        past_epoch_statuses=["confirmed_gap"],
        current_status="suspected_gap",
        current_epoch_answers=1,
    ) is True

    # Past gap but 0 answers in current epoch -> False
    assert calculate_persistent_gap(
        past_epoch_statuses=["confirmed_gap"],
        current_status="confirmed_gap",
        current_epoch_answers=0,
    ) is False

    # Past was mastered -> False
    assert calculate_persistent_gap(
        past_epoch_statuses=["mastered"],
        current_status="confirmed_gap",
        current_epoch_answers=1,
    ) is False


def test_determine_likely_cause():
    # 1. Prerequisite gap wins first
    cause, also = determine_likely_cause(
        concept_id="D09",
        status="suspected_gap",
        ancestor_statuses={"D08": "confirmed_gap"},
        incorrect_responses=[{"reason_tags": ["rushed"]}],
    )
    assert cause == "prerequisite_gap"
    assert "rushed" in also

    # 2. Misconception
    cause, also = determine_likely_cause(
        concept_id="D02",
        status="suspected_gap",
        ancestor_statuses={"D01": "mastered"},
        incorrect_responses=[
            {"primary_concept_id": "D02", "mapped_concept_id": "D02", "reason_tags": ["misconception", "rushed"]}
        ],
    )
    assert cause == "misconception"

    # 3. Confident error majority
    cause, _ = determine_likely_cause(
        concept_id="D03",
        status="confirmed_gap",
        ancestor_statuses={"D01": "mastered", "D02": "mastered"},
        incorrect_responses=[
            {"reason_tags": ["confident_error"]},
            {"reason_tags": ["confident_error"]},
            {"reason_tags": ["rushed"]},
        ],
    )
    assert cause == "confident_error"

    # 4. Unclear when no dominant cause
    cause, _ = determine_likely_cause(
        concept_id="D03",
        status="suspected_gap",
        ancestor_statuses={},
        incorrect_responses=[{"reason_tags": []}],
    )
    assert cause == "unclear"
