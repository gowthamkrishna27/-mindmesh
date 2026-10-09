"""Evidence weighting and reason tagging service.

Conforms strictly to Specification v3.0 Sections 7.2, 7.3, 7.6.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set
from app.core.settings_rules import (
    BASE_WEIGHT_CORRECT_NOT_SURE,
    BASE_WEIGHT_DEFAULT,
    BASE_WEIGHT_INCORRECT_SURE,
    INDIRECT_CORRECT_MULTIPLIER,
    INDIRECT_INCORRECT_MULTIPLIER,
    MAPPED_MISCONCEPTION_WEIGHT_MULTIPLIER,
    WEIGHT_CLAMP_MAX,
    WEIGHT_CLAMP_MIN,
    W_ASSISTED_CORRECT,
    W_ASSISTED_INCORRECT,
    W_FAST_CORRECT,
    W_FAST_INCORRECT,
    W_HESITATED_CORRECT,
    W_HESITATED_INCORRECT,
    W_SLOW_CORRECT,
    W_SLOW_INCORRECT,
)
from app.services.signals import DerivedSignals


@dataclass(frozen=True)
class GeneratedEvidenceItem:
    """Individual evidence record produced for a concept."""

    concept_id: str
    evidence_type: str  # primary_direct, mapped_misconception, indirect_prerequisite
    direction: str  # positive, negative
    weight: float
    source_concept_id: Optional[str] = None
    edge_prerequisite_id: Optional[str] = None
    edge_dependent_id: Optional[str] = None


def calculate_response_weight(
    is_correct: bool,
    confidence: str,
    signals: DerivedSignals,
    assisted: bool = False,
) -> float:
    """Compute bounded evidence weight according to Section 7.2 rules.

    Clamped to [0.25, 1.20].
    """
    # 1. Base weight
    if is_correct and confidence == "not_sure":
        w = BASE_WEIGHT_CORRECT_NOT_SURE
    elif (not is_correct) and confidence == "sure":
        w = BASE_WEIGHT_INCORRECT_SURE
    else:
        w = BASE_WEIGHT_DEFAULT

    # 2. Multipliers (all that apply)
    if signals.time_class == "fast":
        w *= W_FAST_CORRECT if is_correct else W_FAST_INCORRECT

    if signals.hesitated and not signals.signals_incomplete:
        w *= W_HESITATED_CORRECT if is_correct else W_HESITATED_INCORRECT

    if signals.time_class == "slow":
        w *= W_SLOW_CORRECT if is_correct else W_SLOW_INCORRECT

    if assisted:
        w *= W_ASSISTED_CORRECT if is_correct else W_ASSISTED_INCORRECT

    # 3. Clamp to [0.25, 1.20]
    return max(WEIGHT_CLAMP_MIN, min(WEIGHT_CLAMP_MAX, round(w, 4)))


def derive_reason_tags(
    is_correct: bool,
    confidence: str,
    signals: DerivedSignals,
    selected_option_data: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Derive deterministic per-answer reason tags according to Section 7.6."""
    tags: List[str] = []
    has_mapping = False

    if selected_option_data:
        has_mapping = bool(
            selected_option_data.get("maps_to_concept_id")
            or selected_option_data.get("misconception_code")
        )

    if not is_correct:
        if has_mapping:
            tags.append("misconception")
        elif confidence == "sure":
            tags.append("confident_error")

        if (signals.hesitated or signals.switched_from_correct) and not signals.signals_incomplete:
            tags.append("hesitation")

        if signals.time_class == "fast":
            tags.append("rushed")
        elif signals.time_class == "slow":
            tags.append("slow")
    else:
        # Correct answer
        if (
            confidence == "not_sure"
            or (signals.hesitated and not signals.signals_incomplete)
            or signals.time_class == "slow"
        ):
            tags.append("shaky_correct")

    return tags


def generate_evidence_items(
    primary_concept_id: str,
    is_correct: bool,
    weight: float,
    direct_prerequisites: Set[str],
    selected_option_data: Optional[Dict[str, Any]] = None,
) -> List[GeneratedEvidenceItem]:
    """Generate primary, mapped, and indirect prerequisite evidence items (Sections 7.2, 7.3)."""
    items: List[GeneratedEvidenceItem] = []

    # 1. Primary direct evidence
    items.append(
        GeneratedEvidenceItem(
            concept_id=primary_concept_id,
            evidence_type="primary_direct",
            direction="positive" if is_correct else "negative",
            weight=weight,
            source_concept_id=None,
        )
    )

    # 2. Mapped misconception evidence (if incorrect and distractor maps to a concept)
    if not is_correct and selected_option_data:
        mapped_cid = selected_option_data.get("maps_to_concept_id")
        if mapped_cid and mapped_cid != primary_concept_id:
            mapped_weight = round(MAPPED_MISCONCEPTION_WEIGHT_MULTIPLIER * weight, 4)
            items.append(
                GeneratedEvidenceItem(
                    concept_id=mapped_cid,
                    evidence_type="mapped_misconception",
                    direction="negative",
                    weight=mapped_weight,
                    source_concept_id=primary_concept_id,
                )
            )

    # 3. Indirect prerequisite evidence (direct prerequisites only)
    for prereq_id in sorted(direct_prerequisites):
        if is_correct:
            indirect_w = round(INDIRECT_CORRECT_MULTIPLIER * weight, 4)
            items.append(
                GeneratedEvidenceItem(
                    concept_id=prereq_id,
                    evidence_type="indirect_prerequisite",
                    direction="positive",
                    weight=indirect_w,
                    source_concept_id=primary_concept_id,
                    edge_prerequisite_id=prereq_id,
                    edge_dependent_id=primary_concept_id,
                )
            )
        else:
            indirect_w = round(INDIRECT_INCORRECT_MULTIPLIER * weight, 4)
            items.append(
                GeneratedEvidenceItem(
                    concept_id=prereq_id,
                    evidence_type="indirect_prerequisite",
                    direction="negative",
                    weight=indirect_w,
                    source_concept_id=primary_concept_id,
                    edge_prerequisite_id=prereq_id,
                    edge_dependent_id=primary_concept_id,
                )
            )

    return items
