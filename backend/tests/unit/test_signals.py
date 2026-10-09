"""Unit tests for server-derived interaction signals (Section 7.1)."""

from datetime import datetime, timezone
import pytest
from app.services.signals import derive_signals


def test_time_classes_and_boundaries():
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # 1. Fast: under 3000 ms (e.g. 2500 ms)
    t_fast = datetime(2026, 1, 1, 12, 0, 2, 500000, tzinfo=timezone.utc)
    sig_fast = derive_signals(issued_at=t0, answered_at=t_fast, expected_time_s=30)
    assert sig_fast.time_class == "fast"
    assert sig_fast.response_time_ms == 2500

    # 2. Normal: between 3000 ms and 2 * expected_time_s (e.g. 30s expected -> threshold is 60s)
    t_norm = datetime(2026, 1, 1, 12, 0, 30, tzinfo=timezone.utc)
    sig_norm = derive_signals(issued_at=t0, answered_at=t_norm, expected_time_s=30)
    assert sig_norm.time_class == "normal"
    assert sig_norm.response_time_ms == 30000

    # 3. Slow: over 2 * expected_time_s (e.g. 65s for 30s expected)
    t_slow = datetime(2026, 1, 1, 12, 1, 5, tzinfo=timezone.utc)
    sig_slow = derive_signals(issued_at=t0, answered_at=t_slow, expected_time_s=30)
    assert sig_slow.time_class == "slow"
    assert sig_slow.response_time_ms == 65000

    # 4. Away: over 300,000 ms (5 minutes, e.g. 301 seconds)
    t_away = datetime(2026, 1, 1, 12, 5, 1, tzinfo=timezone.utc)
    sig_away = derive_signals(issued_at=t0, answered_at=t_away, expected_time_s=30)
    assert sig_away.time_class == "away"
    assert sig_away.response_time_ms == 301000


def test_option_changes_counting_and_capping():
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 1, 12, 0, 25, tzinfo=timezone.utc)

    # First interaction + 3 option changes
    events = [
        {"event_type": "first_interaction", "payload": {"to_option_id": "A"}},
        {"event_type": "option_changed", "payload": {"from_option_id": "A", "to_option_id": "B"}},
        {"event_type": "option_changed", "payload": {"from_option_id": "B", "to_option_id": "C"}},
        {"event_type": "option_changed", "payload": {"from_option_id": "C", "to_option_id": "D"}},
    ]
    sig = derive_signals(
        issued_at=t0,
        answered_at=t1,
        expected_time_s=30,
        events=events,
        selected_option_key="D",
        correct_option_key="A",
    )
    assert sig.option_changes == 3
    assert sig.first_selected_option_id == "A"
    assert sig.hesitated is True
    assert sig.switched_from_correct is True
    assert sig.signals_incomplete is False

    # Test capping at 10 changes
    many_events = [{"event_type": "first_interaction", "payload": {"to_option_id": "A"}}] + [
        {"event_type": "option_changed", "payload": {"from_option_id": "A", "to_option_id": "B"}}
        for _ in range(15)
    ]
    sig_capped = derive_signals(
        issued_at=t0,
        answered_at=t1,
        expected_time_s=30,
        events=many_events,
        selected_option_key="B",
        correct_option_key="B",
    )
    assert sig_capped.option_changes == 10


def test_signals_incomplete_when_no_selection_events():
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 1, 12, 0, 15, tzinfo=timezone.utc)

    # No interaction events (dropped network or old client)
    sig = derive_signals(
        issued_at=t0,
        answered_at=t1,
        expected_time_s=30,
        events=[],
        selected_option_key="A",
        correct_option_key="A",
    )
    assert sig.signals_incomplete is True
    assert sig.option_changes == 0
    assert sig.hesitated is False
    assert sig.switched_from_correct is False
    assert sig.first_selected_option_id is None
