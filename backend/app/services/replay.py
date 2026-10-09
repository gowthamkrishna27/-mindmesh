"""Deterministic replay service.

Re-derives student concept mastery, epochs, and evidence from the source-of-truth
response log (Specification v3.0 Sections 7.5, 12, 14).
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session
from app.models.curriculum import Question, QuestionOption
from app.models.engine import Response
from app.services.evidence import (
    GeneratedEvidenceItem,
    calculate_response_weight,
    derive_reason_tags,
    generate_evidence_items,
)
from app.services.graph import GraphService
from app.services.mastery import (
    ConceptMasteryState,
    apply_evidence_item,
    calculate_persistent_gap,
    calculate_retest_outcome,
    calculate_trend,
)
from app.services.signals import DerivedSignals


@dataclass
class EpochSnapshot:
    """Historical record of a concept's state at the end of an evidence epoch."""

    epoch_index: int
    n_direct_answers: int
    final_direct_estimate: float
    final_status: str
    ready: bool


@dataclass
class ReplayResult:
    """Complete replayed mastery state for a student."""

    student_id: str
    current_states: Dict[str, ConceptMasteryState]
    epoch_histories: Dict[str, List[EpochSnapshot]]
    retest_outcomes: Dict[str, Tuple[str, bool]]
    trends: Dict[str, str]
    persistent_gaps: Dict[str, bool]


def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def replay_responses(
    student_id: str,
    responses: List[Any],
    questions_map: Dict[str, Any],
    graph_service: GraphService,
    all_concept_ids: List[str],
    retest_session_ids: Optional[Set[str]] = None,
) -> ReplayResult:
    """Replay an ordered list of response items and reconstruct the exact mastery state."""
    if retest_session_ids is None:
        retest_session_ids = set()

    current_states: Dict[str, ConceptMasteryState] = {
        cid: ConceptMasteryState(concept_id=cid, epoch_index=0) for cid in all_concept_ids
    }
    epoch_histories: Dict[str, List[EpochSnapshot]] = {cid: [] for cid in all_concept_ids}
    sessions_opened_epochs: Set[Tuple[str, str]] = set()  # (session_id, concept_id)

    # Track distinct questions answered per concept in current epoch
    current_epoch_fresh_answers: Dict[str, int] = {cid: 0 for cid in all_concept_ids}
    current_epoch_fresh_correct: Dict[str, int] = {cid: 0 for cid in all_concept_ids}
    current_epoch_fresh_unassisted: Dict[str, int] = {cid: 0 for cid in all_concept_ids}

    for resp in responses:
        qid = _get_val(resp, "question_id")
        session_id = _get_val(resp, "session_id")
        q_obj = questions_map.get(qid)
        if not q_obj:
            continue

        primary_cid = _get_val(q_obj, "primary_concept_id")
        is_retest_session = session_id in retest_session_ids

        # 1. Epoch transition rule (Section 7.5):
        # The first answer in a retest session whose primary concept is C opens a new epoch for C.
        if is_retest_session and primary_cid:
            session_key = (session_id, primary_cid)
            if session_key not in sessions_opened_epochs:
                sessions_opened_epochs.add(session_key)

                # Snapshot the prior epoch
                old_state = current_states[primary_cid]
                epoch_histories[primary_cid].append(
                    EpochSnapshot(
                        epoch_index=old_state.epoch_index,
                        n_direct_answers=old_state.n_direct_questions,
                        final_direct_estimate=old_state.direct_estimate,
                        final_status=old_state.status,
                        ready=old_state.ready,
                    )
                )

                # Open new epoch for primary concept C only
                new_epoch_idx = old_state.epoch_index + 1
                current_states[primary_cid] = ConceptMasteryState(
                    concept_id=primary_cid,
                    epoch_index=new_epoch_idx,
                )
                current_epoch_fresh_answers[primary_cid] = 0
                current_epoch_fresh_correct[primary_cid] = 0
                current_epoch_fresh_unassisted[primary_cid] = 0

        # 2. Extract response attributes
        is_correct = bool(_get_val(resp, "is_correct", False))
        confidence = _get_val(resp, "confidence", "fairly_sure")
        assisted = bool(_get_val(resp, "assisted", False))
        attempt_number = _get_val(resp, "attempt_number", 1)

        # Extract or construct signals
        signals = _get_val(resp, "signals")
        if signals is None:
            time_class = _get_val(resp, "time_class", "normal")
            option_changes = _get_val(resp, "option_changes", 0)
            hesitated = bool(_get_val(resp, "hesitated", option_changes >= 2))
            switched = bool(_get_val(resp, "switched_from_correct", False))
            signals_incomplete = bool(_get_val(resp, "signals_incomplete", False))
            signals = DerivedSignals(
                response_time_ms=_get_val(resp, "response_time_ms", 30000),
                time_class=time_class,
                option_changes=option_changes,
                first_selected_option_id=_get_val(resp, "first_selected_option_id"),
                hesitated=hesitated,
                switched_from_correct=switched,
                signals_incomplete=signals_incomplete,
                client_response_time_ms=None,
            )

        # 3. Calculate weight
        w = calculate_response_weight(
            is_correct=is_correct,
            confidence=confidence,
            signals=signals,
            assisted=assisted,
        )

        # 4. Generate evidence items
        direct_prereqs = graph_service.get_direct_prerequisites(primary_cid) if primary_cid else set()

        # Selected option distractor mapping
        opt_data = None
        selected_key = _get_val(resp, "selected_option_key")
        options = _get_val(q_obj, "options", [])
        for opt in options:
            okey = _get_val(opt, "option_key")
            if okey == selected_key:
                opt_data = {
                    "maps_to_concept_id": _get_val(opt, "maps_to_concept_id"),
                    "misconception_code": _get_val(opt, "misconception_code"),
                }
                break


        evidence_items = generate_evidence_items(
            primary_concept_id=primary_cid,
            is_correct=is_correct,
            weight=w,
            direct_prerequisites=direct_prereqs,
            selected_option_data=opt_data,
        )

        is_repeat = attempt_number > 1

        # Track fresh answers for retest outcome
        if not is_repeat and primary_cid:
            current_epoch_fresh_answers[primary_cid] += 1
            if is_correct:
                current_epoch_fresh_correct[primary_cid] += 1
            if not assisted:
                current_epoch_fresh_unassisted[primary_cid] += 1

        # 5. Apply evidence items to affected concepts' current epochs
        for ev_item in evidence_items:
            cid = ev_item.concept_id
            if cid in current_states:
                apply_evidence_item(
                    state=current_states[cid],
                    item=ev_item,
                    is_assisted=assisted,
                    is_repeat=is_repeat,
                )

    # 6. Calculate trends, persistent gaps, and retest outcomes
    trends: Dict[str, str] = {}
    persistent_gaps: Dict[str, bool] = {}
    retest_outcomes: Dict[str, Tuple[str, bool]] = {}

    for cid in all_concept_ids:
        history = epoch_histories[cid]
        curr_state = current_states[cid]

        # Trend across epochs
        all_estimates = [h.final_direct_estimate for h in history] + [curr_state.direct_estimate]
        trends[cid] = calculate_trend(all_estimates)

        # Persistent gap
        past_statuses = [h.final_status for h in history]
        persistent_gaps[cid] = calculate_persistent_gap(
            past_epoch_statuses=past_statuses,
            current_status=curr_state.status,
            current_epoch_answers=curr_state.n_direct_questions,
        )

        # Retest outcome (comparing previous epoch to current)
        prev_status = history[-1].final_status if history else "unassessed"
        retest_outcomes[cid] = calculate_retest_outcome(
            prev_status=prev_status,
            current_status=curr_state.status,
            fresh_direct_count=current_epoch_fresh_answers[cid],
            fresh_correct_count=current_epoch_fresh_correct[cid],
            fresh_unassisted_count=current_epoch_fresh_unassisted[cid],
        )

    return ReplayResult(
        student_id=student_id,
        current_states=current_states,
        epoch_histories=epoch_histories,
        retest_outcomes=retest_outcomes,
        trends=trends,
        persistent_gaps=persistent_gaps,
    )


def replay_student_mastery_from_db(db: Session, student_id: str) -> ReplayResult:
    """Execute replay for a student from database response records."""
    from app.services.graph import load_graph_from_db

    graph_service = load_graph_from_db(db)
    all_concept_ids = list(graph_service.graph.nodes)

    # Fetch questions map
    questions_list = db.query(Question).all()
    questions_map = {q.id: q for q in questions_list}

    # Fetch responses ordered by id
    responses = (
        db.query(Response)
        .filter(Response.student_id == student_id)
        .order_by(Response.id.asc())
        .all()
    )

    # Identify sessions that contain retest responses
    # In Phase 3, session kind can be inferred from session_id naming or passed set
    retest_session_ids = {r.session_id for r in responses if "retest" in r.session_id.lower()}

    return replay_responses(
        student_id=student_id,
        responses=responses,
        questions_map=questions_map,
        graph_service=graph_service,
        all_concept_ids=all_concept_ids,
        retest_session_ids=retest_session_ids,
    )
