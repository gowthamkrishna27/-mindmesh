"""Unit tests for evidence weighting and reason tags (Sections 7.2, 7.3, 7.6)."""

import pytest
from app.services.evidence import (
    calculate_response_weight,
    derive_reason_tags,
    generate_evidence_items,
)
from app.services.signals import DerivedSignals


def make_signals(
    time_class: str = "normal",
    hesitated: bool = False,
    switched_from_correct: bool = False,
    signals_incomplete: bool = False,
) -> DerivedSignals:
    return DerivedSignals(
        response_time_ms=20000,
        time_class=time_class,
        option_changes=2 if hesitated else 0,
        first_selected_option_id="A",
        hesitated=hesitated,
        switched_from_correct=switched_from_correct,
        signals_incomplete=signals_incomplete,
        client_response_time_ms=None,
    )


def test_base_weights():
    norm_sig = make_signals()

    # Normal default
    assert calculate_response_weight(is_correct=True, confidence="fairly_sure", signals=norm_sig) == 1.0
    assert calculate_response_weight(is_correct=False, confidence="fairly_sure", signals=norm_sig) == 1.0

    # Correct and not_sure = 0.60
    assert calculate_response_weight(is_correct=True, confidence="not_sure", signals=norm_sig) == 0.60

    # Incorrect and sure = 1.20
    assert calculate_response_weight(is_correct=False, confidence="sure", signals=norm_sig) == 1.20


def test_signal_multipliers_and_clamping():
    # Fast: x 0.70
    fast_sig = make_signals(time_class="fast")
    assert pytest.approx(calculate_response_weight(is_correct=True, confidence="fairly_sure", signals=fast_sig)) == 0.70
    assert pytest.approx(calculate_response_weight(is_correct=False, confidence="fairly_sure", signals=fast_sig)) == 0.70

    # Hesitated: correct x 0.85, incorrect x 0.90
    hes_sig = make_signals(hesitated=True)
    assert pytest.approx(calculate_response_weight(is_correct=True, confidence="fairly_sure", signals=hes_sig)) == 0.85
    assert pytest.approx(calculate_response_weight(is_correct=False, confidence="fairly_sure", signals=hes_sig)) == 0.90

    # Slow: correct x 0.85, incorrect x 1.00
    slow_sig = make_signals(time_class="slow")
    assert pytest.approx(calculate_response_weight(is_correct=True, confidence="fairly_sure", signals=slow_sig)) == 0.85
    assert pytest.approx(calculate_response_weight(is_correct=False, confidence="fairly_sure", signals=slow_sig)) == 1.00

    # Assisted: x 0.50
    assert pytest.approx(calculate_response_weight(is_correct=True, confidence="fairly_sure", signals=make_signals(), assisted=True)) == 0.50

    # Clamping floor (0.25)
    # e.g. correct + not_sure (0.6) * fast (0.7) * assisted (0.5) = 0.21 -> clamped to 0.25
    assert calculate_response_weight(is_correct=True, confidence="not_sure", signals=fast_sig, assisted=True) == 0.25

    # Clamping ceiling (1.20)
    # e.g. incorrect + sure (1.2) -> 1.20
    sure_sig = make_signals(time_class="normal")
    assert calculate_response_weight(is_correct=False, confidence="sure", signals=sure_sig) == 1.20


def test_derive_reason_tags():
    # Misconception tag
    distractor_data = {"maps_to_concept_id": "D02", "misconception_code": "WRONG_MODEL"}
    tags_misc = derive_reason_tags(
        is_correct=False,
        confidence="fairly_sure",
        signals=make_signals(),
        selected_option_data=distractor_data,
    )
    assert "misconception" in tags_misc

    # Confident error
    tags_conf = derive_reason_tags(
        is_correct=False,
        confidence="sure",
        signals=make_signals(),
        selected_option_data=None,
    )
    assert "confident_error" in tags_conf

    # Hesitation
    tags_hes = derive_reason_tags(
        is_correct=False,
        confidence="fairly_sure",
        signals=make_signals(hesitated=True),
    )
    assert "hesitation" in tags_hes

    # Rushed
    tags_rush = derive_reason_tags(
        is_correct=False,
        confidence="fairly_sure",
        signals=make_signals(time_class="fast"),
    )
    assert "rushed" in tags_rush

    # Shaky correct
    tags_shaky = derive_reason_tags(
        is_correct=True,
        confidence="not_sure",
        signals=make_signals(),
    )
    assert "shaky_correct" in tags_shaky


def test_generate_evidence_items():
    # Primary direct + mapped misconception + indirect prerequisite
    items = generate_evidence_items(
        primary_concept_id="D09",
        is_correct=False,
        weight=1.0,
        direct_prerequisites={"D08"},
        selected_option_data={"maps_to_concept_id": "D04", "misconception_code": "FK_MISUNDERSTOOD"},
    )

    # 1. Primary direct: D09, negative, weight 1.0
    primary = next(i for i in items if i.evidence_type == "primary_direct")
    assert primary.concept_id == "D09"
    assert primary.direction == "negative"
    assert primary.weight == 1.0

    # 2. Mapped misconception: D04, negative, weight 0.5
    mapped = next(i for i in items if i.evidence_type == "mapped_misconception")
    assert mapped.concept_id == "D04"
    assert mapped.direction == "negative"
    assert mapped.weight == 0.5

    # 3. Indirect prerequisite: D08, negative, weight 0.3
    indirect = next(i for i in items if i.evidence_type == "indirect_prerequisite")
    assert indirect.concept_id == "D08"
    assert indirect.direction == "negative"
    assert indirect.weight == 0.3
