"""Deterministic diagnosis, evidence, and adaptive selection rules and thresholds.

Source of truth: MindMesh Backend Specification v3.0 (Sections 5, 7, 8, 9).
All thresholds must remain in this file to preserve maintainability and auditability.
"""

from typing import Final, Mapping

# --- Section 7.1 & 7.2: Timing and Signal Boundaries ---
FAST_MS: Final[int] = 3000
SLOW_MULTIPLIER: Final[float] = 2.0
IDLE_CAP_MS: Final[int] = 300000  # 5 minutes, treated as inactivity (away)
HESITATION_MIN_CHANGES: Final[int] = 2
OPTION_CHANGES_CAP: Final[int] = 10

# Expected duration by question difficulty level (1-5), in seconds
EXPECTED_TIME_BY_DIFFICULTY: Final[Mapping[int, int]] = {
    1: 20,
    2: 30,
    3: 45,
    4: 60,
    5: 90,
}

# --- Section 7.2: Weights and Clamping ---
BASE_WEIGHT_DEFAULT: Final[float] = 1.0
BASE_WEIGHT_CORRECT_NOT_SURE: Final[float] = 0.60
BASE_WEIGHT_INCORRECT_SURE: Final[float] = 1.20

W_FAST_CORRECT: Final[float] = 0.70
W_FAST_INCORRECT: Final[float] = 0.70
W_HESITATED_CORRECT: Final[float] = 0.85
W_HESITATED_INCORRECT: Final[float] = 0.90
W_SLOW_CORRECT: Final[float] = 0.85
W_SLOW_INCORRECT: Final[float] = 1.00
W_ASSISTED_CORRECT: Final[float] = 0.50
W_ASSISTED_INCORRECT: Final[float] = 0.50

WEIGHT_CLAMP_MIN: Final[float] = 0.25
WEIGHT_CLAMP_MAX: Final[float] = 1.20

# Initial prior weights (start at 0.5: 1.0 / (1.0 + 1.0))
INITIAL_PRIOR_WEIGHT_CORRECT: Final[float] = 1.0
INITIAL_PRIOR_WEIGHT_INCORRECT: Final[float] = 1.0

# --- Section 7.2: Mapped Misconceptions ---
MAPPED_MISCONCEPTION_WEIGHT_MULTIPLIER: Final[float] = 0.50

# --- Section 7.3: Indirect Prerequisite Evidence ---
INDIRECT_INCORRECT_MULTIPLIER: Final[float] = 0.30
INDIRECT_CORRECT_MULTIPLIER: Final[float] = 0.15

# --- Section 7.4: Status Rules & Readiness ---
CONFIRMED_GAP_MAX_DIRECT_ESTIMATE: Final[float] = 0.30
CONFIRMED_GAP_MIN_QUESTIONS: Final[int] = 3
CONFIRMED_GAP_MIN_PRIMARY_QUESTIONS: Final[int] = 2

MASTERED_MIN_DIRECT_ESTIMATE: Final[float] = 0.70
MASTERED_MIN_QUESTIONS: Final[int] = 2
MASTERED_MIN_CORRECT: Final[int] = 2

SUSPECTED_GAP_DIRECT_THRESHOLD: Final[float] = 0.40
SUSPECTED_GAP_BLENDED_THRESHOLD: Final[float] = 0.40

READY_MIN_ESTIMATE: Final[float] = 0.60
FAILED_CONCEPT_ESTIMATE_THRESHOLD: Final[float] = 0.50

# --- Section 7.7: Attempt History & Trends ---
TREND_DELTA: Final[float] = 0.10

# --- Section 5.3: Question Bank & Session Budget Limits ---
MAX_DIAGNOSTIC_QUESTIONS_PER_CONCEPT: Final[int] = 3
MAX_DIAGNOSTIC_SESSION_QUESTIONS: Final[int] = 12
DEFAULT_MIN_QUESTIONS_PER_CONCEPT: Final[int] = 5
DEFAULT_MIN_RETEST_ITEMS_PER_CONCEPT: Final[int] = 2

# --- Section 8.3: Selection Ranking Weights ---
RANK_WEIGHT_U: Final[float] = 0.40  # Uncertainty
RANK_WEIGHT_I: Final[float] = 0.25  # Importance / descendant coverage
RANK_WEIGHT_S: Final[float] = 0.25  # Struggle evidence
RANK_WEIGHT_C: Final[float] = 0.10  # Branch coverage bonus
PREREQUISITE_FAILED_BONUS: Final[float] = 0.25
