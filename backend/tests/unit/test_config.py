"""Unit tests for configuration and deterministic settings rules."""

from app.core.config import settings
from app.core import settings_rules


def test_settings_defaults():
    assert settings.PROJECT_NAME == "MindMesh"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.LLM_ENABLED is False
    assert settings.MIN_QUESTIONS_PER_CONCEPT >= 4
    assert settings.MIN_RETEST_ITEMS_PER_CONCEPT >= 1


def test_deterministic_rules_thresholds_match_spec_v3():
    """Verify that all deterministic thresholds match Specification v3 exact values."""
    # Timing boundaries (Section 7.1)
    assert settings_rules.FAST_MS == 3000
    assert settings_rules.IDLE_CAP_MS == 300000
    assert settings_rules.SLOW_MULTIPLIER == 2.0
    assert settings_rules.HESITATION_MIN_CHANGES == 2

    # Weight adjustments & clamp (Section 7.2)
    assert settings_rules.BASE_WEIGHT_DEFAULT == 1.0
    assert settings_rules.BASE_WEIGHT_CORRECT_NOT_SURE == 0.60
    assert settings_rules.BASE_WEIGHT_INCORRECT_SURE == 1.20
    assert settings_rules.WEIGHT_CLAMP_MIN == 0.25
    assert settings_rules.WEIGHT_CLAMP_MAX == 1.20

    # Multipliers
    assert settings_rules.W_FAST_CORRECT == 0.70
    assert settings_rules.W_FAST_INCORRECT == 0.70
    assert settings_rules.W_HESITATED_CORRECT == 0.85
    assert settings_rules.W_HESITATED_INCORRECT == 0.90
    assert settings_rules.W_SLOW_CORRECT == 0.85
    assert settings_rules.W_SLOW_INCORRECT == 1.00
    assert settings_rules.W_ASSISTED_CORRECT == 0.50
    assert settings_rules.W_ASSISTED_INCORRECT == 0.50

    # Indirect evidence (Section 7.3)
    assert settings_rules.INDIRECT_INCORRECT_MULTIPLIER == 0.30
    assert settings_rules.INDIRECT_CORRECT_MULTIPLIER == 0.15

    # Status rules thresholds (Section 7.4)
    assert settings_rules.CONFIRMED_GAP_MAX_DIRECT_ESTIMATE == 0.30
    assert settings_rules.CONFIRMED_GAP_MIN_QUESTIONS == 3
    assert settings_rules.CONFIRMED_GAP_MIN_PRIMARY_QUESTIONS == 2
    assert settings_rules.MASTERED_MIN_DIRECT_ESTIMATE == 0.70
    assert settings_rules.MASTERED_MIN_QUESTIONS == 2
    assert settings_rules.MASTERED_MIN_CORRECT == 2
    assert settings_rules.SUSPECTED_GAP_DIRECT_THRESHOLD == 0.40
    assert settings_rules.READY_MIN_ESTIMATE == 0.60

    # Expected time mapping
    assert settings_rules.EXPECTED_TIME_BY_DIFFICULTY[1] == 20
    assert settings_rules.EXPECTED_TIME_BY_DIFFICULTY[2] == 30
    assert settings_rules.EXPECTED_TIME_BY_DIFFICULTY[3] == 45
    assert settings_rules.EXPECTED_TIME_BY_DIFFICULTY[4] == 60
    assert settings_rules.EXPECTED_TIME_BY_DIFFICULTY[5] == 90

    # Selection weights (Section 8.3)
    assert settings_rules.RANK_WEIGHT_U == 0.40
    assert settings_rules.RANK_WEIGHT_I == 0.25
    assert settings_rules.RANK_WEIGHT_S == 0.25
    assert settings_rules.RANK_WEIGHT_C == 0.10
