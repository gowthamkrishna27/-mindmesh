"""Unit tests replicating every hand-checked example from Section 7.4.

Hand-checked table (Section 7.4):
| Direct answers | Estimate | Status | Ready |
| wrong | 0.333 | suspected_gap | no |
| wrong, wrong | 0.250 | suspected_gap | no |
| wrong x3 | 0.200 | confirmed_gap | no |
| wrong x3, all fast (0.7) | 0.244 | confirmed_gap | no |
| wrong x3, all hesitated (0.9) | 0.213 | confirmed_gap | no |
| wrong, hesitated (0.9) | 0.345 | suspected_gap | no |
| right | 0.667 | uncertain | yes |
| right, hesitated (0.85) | 0.649 | uncertain | yes |
| right, right | 0.750 | mastered | yes |
| right, right, both hesitated (0.85) | 0.730 | mastered | yes |
| right, right, both not_sure (0.6) | 0.6875 | uncertain | yes |
| right, right, both not_sure and hesitated (0.51) | 0.669 | uncertain | yes |
| right, wrong | 0.500 | uncertain | no |
| wrong, wrong, right | 0.400 | uncertain | no |
| right, right, wrong | 0.600 | uncertain | no |
"""

import pytest
from app.services.evidence import GeneratedEvidenceItem
from app.services.mastery import ConceptMasteryState, apply_evidence_item


def simulate_direct_answers(answers: list[tuple[bool, float]]) -> ConceptMasteryState:
    """Helper to simulate a sequence of direct answers: [(is_correct, weight), ...]."""
    state = ConceptMasteryState(concept_id="TEST")
    for is_correct, weight in answers:
        item = GeneratedEvidenceItem(
            concept_id="TEST",
            evidence_type="primary_direct",
            direction="positive" if is_correct else "negative",
            weight=weight,
        )
        apply_evidence_item(state, item, is_assisted=False, is_repeat=False)
    return state


def test_row_1_wrong():
    state = simulate_direct_answers([(False, 1.0)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.333
    assert state.status == "suspected_gap"
    assert state.ready is False


def test_row_2_wrong_wrong():
    state = simulate_direct_answers([(False, 1.0), (False, 1.0)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.250
    assert state.status == "suspected_gap"
    assert state.ready is False


def test_row_3_wrong_x3():
    state = simulate_direct_answers([(False, 1.0), (False, 1.0), (False, 1.0)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.200
    assert state.status == "confirmed_gap"
    assert state.ready is False


def test_row_4_wrong_x3_all_fast():
    state = simulate_direct_answers([(False, 0.7), (False, 0.7), (False, 0.7)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.244
    assert state.status == "confirmed_gap"
    assert state.ready is False


def test_row_5_wrong_x3_all_hesitated():
    state = simulate_direct_answers([(False, 0.9), (False, 0.9), (False, 0.9)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.213
    assert state.status == "confirmed_gap"
    assert state.ready is False


def test_row_6_wrong_hesitated():
    state = simulate_direct_answers([(False, 0.9)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.345
    assert state.status == "suspected_gap"
    assert state.ready is False


def test_row_7_right():
    state = simulate_direct_answers([(True, 1.0)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.667
    assert state.status == "uncertain"
    assert state.ready is True


def test_row_8_right_hesitated():
    state = simulate_direct_answers([(True, 0.85)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.649
    assert state.status == "uncertain"
    assert state.ready is True


def test_row_9_right_right():
    state = simulate_direct_answers([(True, 1.0), (True, 1.0)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.750
    assert state.status == "mastered"
    assert state.ready is True


def test_row_10_right_right_both_hesitated():
    state = simulate_direct_answers([(True, 0.85), (True, 0.85)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.730
    assert state.status == "mastered"
    assert state.ready is True


def test_row_11_right_right_both_not_sure():
    state = simulate_direct_answers([(True, 0.6), (True, 0.6)])
    assert pytest.approx(state.direct_estimate, 0.0001) == 0.6875
    assert state.status == "uncertain"
    assert state.ready is True


def test_row_12_right_right_both_not_sure_and_hesitated():
    state = simulate_direct_answers([(True, 0.51), (True, 0.51)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.669
    assert state.status == "uncertain"
    assert state.ready is True


def test_row_13_right_wrong():
    state = simulate_direct_answers([(True, 1.0), (False, 1.0)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.500
    assert state.status == "uncertain"
    assert state.ready is False


def test_row_14_wrong_wrong_right():
    state = simulate_direct_answers([(False, 1.0), (False, 1.0), (True, 1.0)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.400
    assert state.status == "uncertain"
    assert state.ready is False


def test_row_15_right_right_wrong():
    state = simulate_direct_answers([(True, 1.0), (True, 1.0), (False, 1.0)])
    assert pytest.approx(state.direct_estimate, 0.001) == 0.600
    assert state.status == "uncertain"
    assert state.ready is False


def test_indirect_evidence_cannot_confirm_mastery_regression():
    """Regression test from Section 7.4:

    Two not_sure correct answers = 0.6875.
    Adding positive indirect evidence lifts blended estimate > 0.70, but status MUST stay uncertain!
    """
    state = simulate_direct_answers([(True, 0.6), (True, 0.6)])
    assert state.direct_estimate == 0.6875
    assert state.status == "uncertain"

    # Add indirect prerequisite positive evidence
    indirect_item = GeneratedEvidenceItem(
        concept_id="TEST",
        evidence_type="indirect_prerequisite",
        direction="positive",
        weight=0.15,
    )
    apply_evidence_item(state, indirect_item)

    # Blended estimate is lifted > 0.70
    assert state.mastery_estimate > 0.70
    # Direct estimate and status MUST NOT be changed to mastered!
    assert state.direct_estimate == 0.6875
    assert state.status == "uncertain"
    assert state.ready is True


def test_mapped_misconception_confirmation_boundary():
    """Third question can be mapped, but two mapped questions cannot confirm a gap."""
    state = ConceptMasteryState(concept_id="TEST")

    # 2 primary wrong + 1 mapped wrong = 3 distinct direct questions, 2 primary -> confirmed_gap
    apply_evidence_item(state, GeneratedEvidenceItem("TEST", "primary_direct", "negative", 1.0))
    apply_evidence_item(state, GeneratedEvidenceItem("TEST", "primary_direct", "negative", 1.0))
    apply_evidence_item(state, GeneratedEvidenceItem("TEST", "mapped_misconception", "negative", 1.0))
    assert state.n_direct_primary == 2
    assert state.n_direct_mapped == 1
    assert state.direct_estimate < 0.30
    assert state.status == "confirmed_gap"

    # 1 primary wrong + 2 mapped wrong -> cannot confirm gap (needs n_direct_primary >= 2)
    state2 = ConceptMasteryState(concept_id="TEST2")
    apply_evidence_item(state2, GeneratedEvidenceItem("TEST2", "primary_direct", "negative", 1.0))
    apply_evidence_item(state2, GeneratedEvidenceItem("TEST2", "mapped_misconception", "negative", 1.0))
    apply_evidence_item(state2, GeneratedEvidenceItem("TEST2", "mapped_misconception", "negative", 1.0))
    assert state2.n_direct_primary == 1
    assert state2.status == "suspected_gap"  # Not confirmed!


def test_repeated_attempts_add_no_evidence():
    state = ConceptMasteryState(concept_id="TEST")
    item = GeneratedEvidenceItem("TEST", "primary_direct", "positive", 1.0)

    # First attempt
    apply_evidence_item(state, item, is_repeat=False)
    assert state.n_direct_questions == 1
    assert state.direct_estimate > 0.5

    # Second attempt on same question
    apply_evidence_item(state, item, is_repeat=True)
    assert state.n_direct_questions == 1  # Not incremented
    assert state.direct_weighted_correct == 2.0  # Not incremented
