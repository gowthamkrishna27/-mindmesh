"""Mastery estimates, status rules, readiness, epochs, and retest outcome engine.

Conforms strictly to Specification v3.0 Sections 7.4, 7.5, 7.6, 7.7.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from app.core.settings_rules import (
    CONFIRMED_GAP_MAX_DIRECT_ESTIMATE,
    CONFIRMED_GAP_MIN_PRIMARY_QUESTIONS,
    CONFIRMED_GAP_MIN_QUESTIONS,
    INITIAL_PRIOR_WEIGHT_CORRECT,
    INITIAL_PRIOR_WEIGHT_INCORRECT,
    MASTERED_MIN_CORRECT,
    MASTERED_MIN_DIRECT_ESTIMATE,
    MASTERED_MIN_QUESTIONS,
    READY_MIN_ESTIMATE,
    SUSPECTED_GAP_BLENDED_THRESHOLD,
    SUSPECTED_GAP_DIRECT_THRESHOLD,
    TREND_DELTA,
)
from app.services.evidence import GeneratedEvidenceItem

# Status ranking for retest comparison (Section 7.5)
# Lower rank number represents better mastery:
# confirmed_gap (3) > suspected_gap (2) > uncertain (1) > mastered (0)
STATUS_RANK: Dict[str, int] = {
    "confirmed_gap": 3,
    "suspected_gap": 2,
    "uncertain": 1,
    "mastered": 0,
    "unassessed": 99,
}


@dataclass
class ConceptMasteryState:
    """Accumulated state, running weights, estimates, and status for a single concept in an epoch."""

    concept_id: str
    epoch_index: int = 0

    # Blended weights (includes indirect evidence)
    weighted_correct: float = INITIAL_PRIOR_WEIGHT_CORRECT
    weighted_incorrect: float = INITIAL_PRIOR_WEIGHT_INCORRECT

    # Direct weights (direct primary + mapped misconception only)
    direct_weighted_correct: float = INITIAL_PRIOR_WEIGHT_CORRECT
    direct_weighted_incorrect: float = INITIAL_PRIOR_WEIGHT_INCORRECT

    # Distinct direct question counts in current epoch
    n_direct_questions: int = 0
    n_direct_correct: int = 0
    n_direct_incorrect: int = 0
    n_direct_unassisted: int = 0
    n_direct_correct_unassisted: int = 0
    n_direct_primary: int = 0
    n_direct_mapped: int = 0
    n_indirect: int = 0

    # Calculated metrics
    mastery_estimate: float = 0.5
    direct_estimate: float = 0.5
    status: str = "unassessed"
    ready: bool = False

    def __post_init__(self) -> None:
        self.recalculate()

    def recalculate(self) -> None:
        """Derive estimates, status, and readiness from current weights and counts."""
        # 1. Estimates (Section 7.4)
        total_blended = self.weighted_correct + self.weighted_incorrect
        self.mastery_estimate = (
            round(self.weighted_correct / total_blended, 4) if total_blended > 0 else 0.5
        )

        total_direct = self.direct_weighted_correct + self.direct_weighted_incorrect
        self.direct_estimate = (
            round(self.direct_weighted_correct / total_direct, 4) if total_direct > 0 else 0.5
        )

        # 2. Status Rules (Section 7.4 evaluated in strict order)
        # Rule 1: unassessed
        if self.n_direct_questions == 0 and self.n_indirect == 0:
            self.status = "unassessed"
        # Rule 2: confirmed_gap
        elif (
            self.n_direct_questions >= CONFIRMED_GAP_MIN_QUESTIONS
            and self.n_direct_correct == 0
            and self.n_direct_unassisted >= CONFIRMED_GAP_MIN_QUESTIONS
            and self.n_direct_primary >= CONFIRMED_GAP_MIN_PRIMARY_QUESTIONS
            and self.direct_estimate < CONFIRMED_GAP_MAX_DIRECT_ESTIMATE
        ):
            self.status = "confirmed_gap"
        # Rule 3: mastered
        elif (
            self.n_direct_questions >= MASTERED_MIN_QUESTIONS
            and self.n_direct_correct >= MASTERED_MIN_CORRECT
            and self.direct_estimate > MASTERED_MIN_DIRECT_ESTIMATE
        ):
            self.status = "mastered"
        # Rule 4: suspected_gap (a or b)
        elif (
            self.n_direct_incorrect >= 1
            and self.direct_estimate < SUSPECTED_GAP_DIRECT_THRESHOLD
        ) or (
            self.n_direct_questions == 0
            and self.n_indirect > 0
            and self.mastery_estimate < SUSPECTED_GAP_BLENDED_THRESHOLD
        ):
            self.status = "suspected_gap"
        # Rule 5: uncertain
        else:
            self.status = "uncertain"

        # 3. Readiness (Section 7.4)
        if self.status == "mastered":
            self.ready = True
        elif (
            self.n_direct_incorrect == 0
            and self.n_direct_correct_unassisted >= 1
            and self.direct_estimate >= READY_MIN_ESTIMATE
        ):
            self.ready = True
        else:
            self.ready = False


def apply_evidence_item(
    state: ConceptMasteryState,
    item: GeneratedEvidenceItem,
    is_assisted: bool = False,
    is_repeat: bool = False,
) -> None:
    """Apply an individual evidence item to update concept weights and counts.

    Repeated attempts (attempt_number > 1) add no evidence.
    """
    if is_repeat:
        return

    if item.evidence_type == "primary_direct":
        state.n_direct_questions += 1
        state.n_direct_primary += 1
        if not is_assisted:
            state.n_direct_unassisted += 1

        if item.direction == "positive":
            state.weighted_correct += item.weight
            state.direct_weighted_correct += item.weight
            state.n_direct_correct += 1
            if not is_assisted:
                state.n_direct_correct_unassisted += 1
        else:
            state.weighted_incorrect += item.weight
            state.direct_weighted_incorrect += item.weight
            state.n_direct_incorrect += 1

    elif item.evidence_type == "mapped_misconception":
        state.n_direct_questions += 1
        state.n_direct_mapped += 1
        state.n_direct_incorrect += 1
        if not is_assisted:
            state.n_direct_unassisted += 1
        state.weighted_incorrect += item.weight
        state.direct_weighted_incorrect += item.weight

    elif item.evidence_type == "indirect_prerequisite":
        state.n_indirect += 1
        if item.direction == "positive":
            state.weighted_correct += item.weight
        else:
            state.weighted_incorrect += item.weight

    state.recalculate()


def calculate_retest_outcome(
    prev_status: str,
    current_status: str,
    fresh_direct_count: int,
    fresh_correct_count: int,
    fresh_unassisted_count: int,
) -> Tuple[str, bool]:
    """Derive retest outcome label and verification_limited flag (Section 7.5).

    Returns:
        (outcome, verification_limited)
        outcome in ("recovered", "improving", "no_change", "declined", "not_verified")
    """
    verification_limited = fresh_unassisted_count < 2

    # 1. No fresh answers
    if fresh_direct_count == 0:
        return "not_verified", verification_limited

    prev_rank = STATUS_RANK.get(prev_status, 99)
    curr_rank = STATUS_RANK.get(current_status, 99)

    # 2. All fresh answers incorrect
    if fresh_correct_count == 0:
        if prev_rank >= 2:  # was confirmed_gap or suspected_gap
            outcome = "no_change"
        else:
            outcome = "declined"
        return outcome, verification_limited

    # 3. At least one fresh correct answer
    if current_status == "mastered":
        outcome = "recovered"
    elif curr_rank < prev_rank:
        outcome = "improving"
    elif curr_rank == prev_rank:
        outcome = "no_change"
    else:
        outcome = "declined"

    return outcome, verification_limited


def calculate_trend(epoch_direct_estimates: List[float]) -> str:
    """Calculate trend between the last two epochs' final direct estimates (Section 7.7).

    Returns:
        "improving", "declining", "flat", or "none"
    """
    if len(epoch_direct_estimates) < 2:
        return "none"

    curr_est = epoch_direct_estimates[-1]
    prev_est = epoch_direct_estimates[-2]
    delta = curr_est - prev_est

    if delta >= TREND_DELTA:
        return "improving"
    if delta <= -TREND_DELTA:
        return "declining"
    return "flat"


def calculate_persistent_gap(
    past_epoch_statuses: List[str],
    current_status: str,
    current_epoch_answers: int,
) -> bool:
    """True when a past epoch ended in a gap and the current epoch also ends in a gap (Section 7.7)."""
    if current_epoch_answers == 0:
        return False

    gap_statuses = {"confirmed_gap", "suspected_gap"}
    had_past_gap = any(s in gap_statuses for s in past_epoch_statuses)
    is_current_gap = current_status in gap_statuses

    return had_past_gap and is_current_gap


def determine_likely_cause(
    concept_id: str,
    status: str,
    ancestor_statuses: Dict[str, str],
    incorrect_responses: List[Dict[str, Any]],
) -> Tuple[Optional[str], List[str]]:
    """Determine likely cause and also_observed descriptions for gaps (Section 7.6).

    Evaluated in order:
    1. prerequisite_gap
    2. misconception
    3. confident_error
    4. hesitation
    5. rushed
    6. unclear
    """
    if status not in ("confirmed_gap", "suspected_gap"):
        return None, []

    candidates: List[str] = []

    # 1. Prerequisite gap: an ancestor has confirmed_gap or suspected_gap
    has_prereq_gap = any(
        s in ("confirmed_gap", "suspected_gap") for s in ancestor_statuses.values()
    )
    if has_prereq_gap:
        candidates.append("prerequisite_gap")

    total_incorrect = len(incorrect_responses)

    if total_incorrect > 0:
        # 2. Misconception: at least one incorrect direct answer with mapped concept == this concept
        has_misconception = any(
            "misconception" in r.get("reason_tags", [])
            and (
                r.get("mapped_concept_id") == concept_id
                or r.get("primary_concept_id") == concept_id
            )
            for r in incorrect_responses
        )
        if has_misconception:
            candidates.append("misconception")

        # 3. Confident error (> 50% of incorrect direct answers)
        count_confident = sum(
            1 for r in incorrect_responses if "confident_error" in r.get("reason_tags", [])
        )
        if count_confident > total_incorrect / 2.0:
            candidates.append("confident_error")

        # 4. Hesitation (> 50% of incorrect direct answers)
        count_hesitation = sum(
            1 for r in incorrect_responses if "hesitation" in r.get("reason_tags", [])
        )
        if count_hesitation > total_incorrect / 2.0:
            candidates.append("hesitation")

        # 5. Rushed (> 50% of incorrect direct answers)
        count_rushed = sum(
            1 for r in incorrect_responses if "rushed" in r.get("reason_tags", [])
        )
        if count_rushed > total_incorrect / 2.0:
            candidates.append("rushed")

    if not candidates:
        return "unclear", []

    primary_cause = candidates[0]
    also_observed = candidates[1:]
    return primary_cause, also_observed
