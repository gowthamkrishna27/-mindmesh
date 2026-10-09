"""Server-derived interaction signals for student responses.

Conforms strictly to Specification v3.0 Section 7.1.
Client-reported timings are never trusted as authoritative.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.core.settings_rules import (
    FAST_MS,
    HESITATION_MIN_CHANGES,
    IDLE_CAP_MS,
    OPTION_CHANGES_CAP,
    SLOW_MULTIPLIER,
)


@dataclass(frozen=True)
class DerivedSignals:
    """Immutable bundle of server-derived response signals."""

    response_time_ms: int
    time_class: str  # fast, normal, slow, away
    option_changes: int
    first_selected_option_id: Optional[str]
    hesitated: bool
    switched_from_correct: bool
    signals_incomplete: bool
    client_response_time_ms: Optional[int]


def derive_signals(
    issued_at: datetime,
    answered_at: datetime,
    expected_time_s: int,
    events: Optional[List[Dict[str, Any]]] = None,
    selected_option_key: str = "",
    correct_option_key: str = "",
    client_response_time_ms: Optional[int] = None,
) -> DerivedSignals:
    """Derive response timing and interaction signals using the server clock and stored events."""
    if events is None:
        events = []

    # 1. Server-measured duration (normalize timezone awareness for database compatibility)
    t_answered = answered_at.replace(tzinfo=None) if answered_at.tzinfo is not None else answered_at
    t_issued = issued_at.replace(tzinfo=None) if issued_at.tzinfo is not None else issued_at
    delta_s = (t_answered - t_issued).total_seconds()
    response_time_ms = max(0, int(delta_s * 1000))

    # 2. Time class categorization
    if response_time_ms < FAST_MS:
        time_class = "fast"
    elif response_time_ms > IDLE_CAP_MS:
        time_class = "away"
    elif response_time_ms > int(SLOW_MULTIPLIER * expected_time_s * 1000):
        time_class = "slow"
    else:
        time_class = "normal"

    # 3. Analyze interaction events
    selection_events: List[Dict[str, Any]] = []
    option_change_events: List[Dict[str, Any]] = []

    for ev in events:
        etype = ev.get("event_type")
        payload = ev.get("payload", {})
        if etype == "option_changed":
            to_opt = payload.get("to_option_id")
            from_opt = payload.get("from_option_id")
            if to_opt:
                selection_events.append(ev)
            if from_opt is not None:
                option_change_events.append(ev)
        elif etype == "first_interaction":
            to_opt = payload.get("to_option_id")
            if to_opt:
                selection_events.append(ev)

    if not selection_events:
        # Incomplete signals: client dropped events or legacy client.
        # No penalty, option change signals treated as absent.
        return DerivedSignals(
            response_time_ms=response_time_ms,
            time_class=time_class,
            option_changes=0,
            first_selected_option_id=None,
            hesitated=False,
            switched_from_correct=False,
            signals_incomplete=True,
            client_response_time_ms=client_response_time_ms,
        )

    # First selected option
    first_selection_payload = selection_events[0].get("payload", {})
    first_selected_option_id = first_selection_payload.get("to_option_id")

    # Count of option_changed events where from_option_id is not null, capped at 10
    raw_changes = len(option_change_events)
    capped_changes = min(OPTION_CHANGES_CAP, raw_changes)

    hesitated = capped_changes >= HESITATION_MIN_CHANGES
    switched_from_correct = (
        bool(first_selected_option_id)
        and (first_selected_option_id == correct_option_key)
        and (selected_option_key != correct_option_key)
    )

    return DerivedSignals(
        response_time_ms=response_time_ms,
        time_class=time_class,
        option_changes=capped_changes,
        first_selected_option_id=first_selected_option_id,
        hesitated=hesitated,
        switched_from_correct=switched_from_correct,
        signals_incomplete=False,
        client_response_time_ms=client_response_time_ms,
    )
