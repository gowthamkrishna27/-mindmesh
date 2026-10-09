"""Student learning, diagnosis, graph, feedback, hints, and reporting endpoints.

Conforms strictly to Specification v3.0 Sections 6, 7.5, 7.6, 9, 10, 11.6 - 11.12.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.auth import get_current_student
from app.db.session import get_db
from app.models.curriculum import Concept, Question, QuestionHint, QuestionOption, Resource
from app.models.engine import Response, ResponseEvidence, StudentConceptMastery
from app.models.session import (
    DiagnosisSnapshot,
    InteractionEvent,
    LearningCompletion,
    Session as AssessmentSession,
    Student,
)
from app.schemas.student import (
    ConceptDetailResponse,
    ConceptReportOut,
    DiagnosisResponse,
    FeedbackResponse,
    GraphEdgeOut,
    GraphNodeOut,
    GraphResponse,
    HintRequest,
    HintResponse,
    HistoricalReportResponse,
    LearningCompleteResponse,
    LearningPathItemOut,
    QuestionFeedbackOut,
    ResourceItemOut,
    RootGapOut,
)
from app.services.diagnosis_service import DiagnosisService
from app.services.graph import load_graph_from_db
from app.services.replay import replay_student_mastery_from_db
from app.services.session_service import utcnow

router = APIRouter(prefix="/students/me", tags=["Student Learning"])


# --- 1. Diagnosis (Section 11.6) ---

@router.get("/diagnosis", response_model=DiagnosisResponse)
def get_diagnosis(
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> DiagnosisResponse:
    """Return the student's latest deterministic diagnosis snapshot and learning path."""
    diag_service = DiagnosisService(db)

    # Find the student's most recently completed diagnostic session
    latest_completed = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.student_id == student.id,
            AssessmentSession.kind == "diagnostic",
            AssessmentSession.status == "completed",
        )
        .order_by(AssessmentSession.completed_at.desc())
        .first()
    )

    if not latest_completed:
        # Define behavior for students with no completed diagnostic session
        graph = load_graph_from_db(db)
        unlocked = graph.get_unlocked_concepts(set())
        return DiagnosisResponse(
            student_id=student.id,
            session_id=None,
            is_finalized=False,
            root_gaps=[],
            weak_concepts=[],
            needs_more_evidence=[],
            learning_path=[],
            unlocked_concepts=unlocked,
            rationale="No completed diagnostic assessment exists yet. Complete a diagnostic to generate a diagnosis.",
        )

    res = diag_service.compute_student_diagnosis(
        student_id=student.id,
        session_id=latest_completed.id,
    )

    return DiagnosisResponse(
        student_id=student.id,
        session_id=latest_completed.id,
        is_finalized=True,
        root_gaps=[
            RootGapOut(
                concept_id=rg.concept_id,
                concept_name=rg.concept_name,
                status=rg.status,
                estimate=rg.estimate,
                ready=rg.ready,
                blocker_score=rg.blocker_score,
                importance=rg.importance,
                failed_dependents_explained=rg.failed_dependents_explained,
                likely_cause=rg.likely_cause,
                also_observed=rg.also_observed,
                signals_summary=rg.signals_summary,
                explanation=rg.explanation,
                recommended_action=rg.recommended_action,
                suggested_depth=rg.suggested_depth,
                prerequisite_path=rg.prerequisite_path,
                evidence_response_ids=rg.evidence_response_ids,
                evidence_question_ids=rg.evidence_question_ids,
            )
            for rg in res.root_gaps
        ],
        weak_concepts=res.weak_concepts,
        needs_more_evidence=res.needs_more_evidence,
        learning_path=[
            LearningPathItemOut(
                concept_id=lp.concept_id,
                concept_name=lp.concept_name,
                kind=lp.kind,
                deferred=lp.deferred,
                recommended_action=lp.recommended_action,
                suggested_depth=lp.suggested_depth,
            )
            for lp in res.learning_path
        ],
        unlocked_concepts=res.unlocked_concepts,
        rationale=res.rationale,
    )


# --- 2. Learning Graph (Section 11.7) ---

@router.get("/graph", response_model=GraphResponse)
def get_student_graph(
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> GraphResponse:
    """Return the student's concept graph with four-state visual status, readiness, and frontier."""
    graph = load_graph_from_db(db)
    concepts_list = db.query(Concept).all()
    concepts_by_id = {c.id: c for c in concepts_list}
    topological_order = graph.get_topological_order()

    # Load student mastery & diagnosis
    mastery_list = (
        db.query(StudentConceptMastery)
        .filter(StudentConceptMastery.student_id == student.id)
        .all()
    )
    mastery_by_id = {m.concept_id: m for m in mastery_list}

    diag_service = DiagnosisService(db)
    diag_res = diag_service.compute_student_diagnosis(student_id=student.id)
    on_path_cids = {item.concept_id for item in diag_res.learning_path}
    root_cause_map = {rg.concept_id: rg.likely_cause for rg in diag_res.root_gaps}

    ready_cids = {cid for cid, m in mastery_by_id.items() if m.ready}
    unlocked_cids = set(graph.get_unlocked_concepts(ready_cids))

    replay_res = replay_student_mastery_from_db(db, student.id)

    nodes: List[GraphNodeOut] = []
    for cid in topological_order:
        c_obj = concepts_by_id[cid]
        m = mastery_by_id.get(cid)
        b_status = m.status if m else "unassessed"

        # Map to 4 visual states (Section 7.4)
        if b_status == "mastered":
            v_status = "mastered"
        elif b_status in ("confirmed_gap", "suspected_gap"):
            v_status = "needs_attention"
        elif b_status == "uncertain":
            v_status = "uncertain"
        else:
            v_status = "unassessed"

        m_est = m.mastery_estimate if m else 0.5
        d_est = m.direct_estimate if m else 0.5
        d_cnt = m.n_direct_questions if m else 0
        is_ready = m.ready if m else False
        is_unlocked = cid in unlocked_cids
        on_path = cid in on_path_cids
        likely_cause = root_cause_map.get(cid, None)
        trend = replay_res.trends.get(cid, "none")

        short_reason = (
            f"Mastered with direct estimate {d_est:.2f}"
            if b_status == "mastered"
            else f"Gap identified ({likely_cause or b_status})"
            if b_status in ("confirmed_gap", "suspected_gap")
            else "Needs more assessment evidence"
            if b_status == "uncertain"
            else "Awaiting assessment"
        )

        nodes.append(
            GraphNodeOut(
                id=cid,
                name=c_obj.name,
                branch=c_obj.branch,
                visual_status=v_status,
                backend_status=b_status,
                mastery_estimate=m_est,
                direct_estimate=d_est,
                direct_count=d_cnt,
                uncertainty_flag=(b_status == "uncertain"),
                short_reason=short_reason,
                on_path=on_path,
                ready=is_ready,
                unlocked=is_unlocked,
                likely_cause=likely_cause,
                trend=trend,
            )
        )

    # Edges
    edges: List[GraphEdgeOut] = [
        GraphEdgeOut(from_concept_id=u, to_concept_id=v)
        for u, v in graph.graph.edges
    ]

    return GraphResponse(nodes=nodes, edges=edges)


# --- 3. Concept Details (Section 11.8) ---

@router.get("/concepts/{id}", response_model=ConceptDetailResponse)
def get_concept_details(
    id: str,
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> ConceptDetailResponse:
    """Return comprehensive concept details, metrics, attempt history, and curated resources."""
    concept = db.query(Concept).filter(Concept.id == id).first()
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CONCEPT_NOT_FOUND", "message": f"Concept '{id}' not found."},
        )

    graph = load_graph_from_db(db)
    mastery = (
        db.query(StudentConceptMastery)
        .filter(
            StudentConceptMastery.student_id == student.id,
            StudentConceptMastery.concept_id == id,
        )
        .first()
    )

    b_status = mastery.status if mastery else "unassessed"
    if b_status == "mastered":
        v_status = "mastered"
    elif b_status in ("confirmed_gap", "suspected_gap"):
        v_status = "needs_attention"
    elif b_status == "uncertain":
        v_status = "uncertain"
    else:
        v_status = "unassessed"

    estimate = mastery.mastery_estimate if mastery else 0.5
    d_estimate = mastery.direct_estimate if mastery else 0.5
    ready = mastery.ready if mastery else False

    # Evidence IDs & Reason tags from responses
    evidence_rows = (
        db.query(ResponseEvidence)
        .filter(
            ResponseEvidence.student_id == student.id,
            ResponseEvidence.concept_id == id,
        )
        .all()
    )
    ev_resp_ids = list({e.response_id for e in evidence_rows})

    responses = (
        db.query(Response)
        .filter(Response.student_id == student.id)
        .all()
    )
    # Filter responses on this concept
    concept_questions = {q.id for q in db.query(Question).filter(Question.primary_concept_id == id).all()}
    concept_responses = [r for r in responses if r.question_id in concept_questions]
    reason_tags = [
        {"response_id": r.id, "tags": r.reason_tags}
        for r in concept_responses
    ]

    # Replay metrics: epochs, trend, persistent_gap
    replay_res = replay_student_mastery_from_db(db, student.id)
    raw_history = replay_res.epoch_histories.get(id, [])
    epoch_history_list = [
        {
            "epoch_index": snap.epoch_index,
            "n_direct_answers": snap.n_direct_answers,
            "final_direct_estimate": snap.final_direct_estimate,
            "final_status": snap.final_status,
            "ready": snap.ready,
        }
        for snap in raw_history
    ]

    attempt_history = {
        "epochs": epoch_history_list,
        "current_epoch": mastery.epoch_index if mastery else 0,
        "trend": replay_res.trends.get(id, "none"),
        "persistent_gap": replay_res.persistent_gaps.get(id, False),
    }

    # Curated resources at 3 depths
    resources_db = db.query(Resource).filter(Resource.concept_id == id).all()
    resources_map: Dict[str, ResourceItemOut] = {}
    for r in resources_db:
        resources_map[r.depth] = ResourceItemOut(
            depth=r.depth,
            title=r.title,
            summary=r.summary,
            content=r.content,
        )
    # Ensure all 3 depths present (placeholder fallback if missing, Section 10)
    for depth in ("quick_revision", "standard", "deep_learning"):
        if depth not in resources_map:
            resources_map[depth] = ResourceItemOut(
                depth=depth,
                title=f"{concept.name} ({depth.replace('_', ' ').title()})",
                summary="Curated resource summary.",
                content="Curated learning content placeholder.",
            )

    diag_service = DiagnosisService(db)
    diag_res = diag_service.compute_student_diagnosis(student_id=student.id)
    root_item = next((rg for rg in diag_res.root_gaps if rg.concept_id == id), None)
    likely_cause = root_item.likely_cause if root_item else None
    suggested_depth = root_item.suggested_depth if root_item else "quick_revision"
    next_action = root_item.recommended_action if root_item else "review_concept"

    return ConceptDetailResponse(
        id=concept.id,
        name=concept.name,
        description=concept.description,
        learning_objective=concept.learning_objective,
        branch=concept.branch,
        visual_status=v_status,
        backend_status=b_status,
        estimate=estimate,
        direct_estimate=d_estimate,
        ready=ready,
        evidence_response_ids=ev_resp_ids,
        reason_tags=reason_tags,
        likely_cause=likely_cause,
        attempt_history=attempt_history,
        reason_text=f"{concept.name} estimated mastery is {d_estimate:.2f} ({v_status}).",
        prerequisites=sorted(graph.get_direct_prerequisites(id)),
        dependents=sorted(graph.get_direct_dependents(id)),
        resources=resources_map,
        suggested_depth=suggested_depth,
        next_action=next_action,
    )


# --- 4. Post-Test Feedback (Section 11.9) ---

@router.get("/feedback", response_model=FeedbackResponse)
def get_feedback(
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> FeedbackResponse:
    """Return detailed post-test question disclosures, correct answers, and explanations.

    CRITICAL: Available ONLY after session completion. Strictly withheld during active sessions.
    """
    # Verify no active diagnostic session
    active_session = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.student_id == student.id,
            AssessmentSession.status == "active",
        )
        .first()
    )
    if active_session and active_session.kind in ("diagnostic", "retest"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "DISCLOSURE_RESTRICTED",
                "message": "Feedback and answer disclosures are restricted while an assessment session is active.",
            },
        )

    # Find the most recently completed diagnostic
    latest_completed = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.student_id == student.id,
            AssessmentSession.kind == "diagnostic",
            AssessmentSession.status == "completed",
        )
        .order_by(AssessmentSession.completed_at.desc())
        .first()
    )
    if not latest_completed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NO_COMPLETED_DIAGNOSTIC",
                "message": "No completed diagnostic assessment found to provide feedback for.",
            },
        )

    # Fetch responses for that session
    session_responses = (
        db.query(Response)
        .filter(Response.session_id == latest_completed.id)
        .order_by(Response.id.asc())
        .all()
    )

    diag_service = DiagnosisService(db)
    diag_res = diag_service.compute_student_diagnosis(
        student_id=student.id,
        session_id=latest_completed.id,
    )
    root_map = {rg.concept_id: rg for rg in diag_res.root_gaps}

    questions_feedback: List[QuestionFeedbackOut] = []
    for r in session_responses:
        q = db.query(Question).filter(Question.id == r.question_id).first()
        if not q:
            continue
        c = db.query(Concept).filter(Concept.id == q.primary_concept_id).first()
        c_name = c.name if c else q.primary_concept_id

        # Correct option key
        correct_opt = (
            db.query(QuestionOption)
            .filter(QuestionOption.question_id == q.id, QuestionOption.is_correct)
            .first()
        )
        correct_key = correct_opt.option_key if correct_opt else ""

        rg = root_map.get(q.primary_concept_id)
        likely_cause = rg.likely_cause if rg else None

        questions_feedback.append(
            QuestionFeedbackOut(
                question_id=q.id,
                concept_id=q.primary_concept_id,
                concept_name=c_name,
                prompt=q.prompt,
                selected_option_key=r.selected_option_key,
                is_correct=r.is_correct,
                correct_option_key=correct_key,
                explanation=q.explanation,
                likely_cause=likely_cause,
                reason_tags=r.reason_tags or [],
            )
        )

    return FeedbackResponse(
        session_id=latest_completed.id,
        completed_at=latest_completed.completed_at.isoformat() if latest_completed.completed_at else None,
        rationale=diag_res.rationale,
        root_gaps=[
            RootGapOut(
                concept_id=rg.concept_id,
                concept_name=rg.concept_name,
                status=rg.status,
                estimate=rg.estimate,
                ready=rg.ready,
                blocker_score=rg.blocker_score,
                importance=rg.importance,
                failed_dependents_explained=rg.failed_dependents_explained,
                likely_cause=rg.likely_cause,
                also_observed=rg.also_observed,
                signals_summary=rg.signals_summary,
                explanation=rg.explanation,
                recommended_action=rg.recommended_action,
                suggested_depth=rg.suggested_depth,
                prerequisite_path=rg.prerequisite_path,
                evidence_response_ids=rg.evidence_response_ids,
                evidence_question_ids=rg.evidence_question_ids,
            )
            for rg in diag_res.root_gaps
        ],
        questions_feedback=questions_feedback,
    )


# --- 5. Progressive Hints (Section 11.10) ---

@router.post("/concepts/{id}/hints", response_model=HintResponse)
def request_hint(
    id: str,
    request: HintRequest,
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> HintResponse:
    """Request progressive level 1 or 2 hints for a concept practice question."""
    # 1. Validate concept and question
    concept = db.query(Concept).filter(Concept.id == id).first()
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CONCEPT_NOT_FOUND", "message": f"Concept '{id}' not found."},
        )

    question = db.query(Question).filter(Question.id == request.question_id).first()
    if not question or question.primary_concept_id != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "QUESTION_CONCEPT_MISMATCH", "message": "Question does not match concept."},
        )

    # 2. Progression enforcement (level 2 requires level 1 first)
    if request.requested_level == 2:
        prior_level1_event = (
            db.query(InteractionEvent)
            .filter(
                InteractionEvent.question_id == request.question_id,
                InteractionEvent.event_type == "hint_requested",
            )
            .all()
        )
        has_level1 = any(
            isinstance(ev.payload, dict) and ev.payload.get("hint_level") == 1
            for ev in prior_level1_event
        )
        if not has_level1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "HINT_LEVEL_ORDER_VIOLATION",
                    "message": "Hint level 1 must be requested before level 2.",
                },
            )

    # 3. Fetch hint content
    hint = (
        db.query(QuestionHint)
        .filter(
            QuestionHint.question_id == request.question_id,
            QuestionHint.hint_level == request.requested_level,
        )
        .first()
    )
    if not hint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "HINT_NOT_FOUND", "message": f"Level {request.requested_level} hint not available."},
        )

    # 4. Record interaction event so subsequent answer is marked assisted
    # Check if student has active session for this question
    active_sess = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.student_id == student.id,
            AssessmentSession.status == "active",
        )
        .first()
    )
    session_id = active_sess.id if active_sess else "practice_direct"
    event = InteractionEvent(
        session_id=session_id,
        question_id=request.question_id,
        event_type="hint_requested",
        payload={"hint_level": request.requested_level},
        server_timestamp=utcnow(),
    )
    db.add(event)
    db.commit()

    return HintResponse(
        question_id=request.question_id,
        concept_id=id,
        hint_level=request.requested_level,
        content=hint.content,
    )


# --- 6. Learning Completion (Section 11.11) ---

@router.post("/learning/{id}/complete", response_model=LearningCompleteResponse)
def complete_learning(
    id: str,
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> LearningCompleteResponse:
    """Mark a learning item/concept complete and enable retesting.

    CRITICAL: Does NOT change mastery estimates, status, or open epochs (Section 6.2 item 6).
    """
    concept = db.query(Concept).filter(Concept.id == id).first()
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CONCEPT_NOT_FOUND", "message": f"Concept '{id}' not found."},
        )

    # Idempotent completion record
    completion = (
        db.query(LearningCompletion)
        .filter(
            LearningCompletion.student_id == student.id,
            LearningCompletion.concept_id == id,
        )
        .first()
    )
    if not completion:
        completion = LearningCompletion(
            student_id=student.id,
            concept_id=id,
            completed_at=utcnow(),
        )
        db.add(completion)
        db.commit()

    # Find or create an enabled retest session
    retest_sess = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.student_id == student.id,
            AssessmentSession.kind == "retest",
            AssessmentSession.status == "active",
        )
        .first()
    )
    if not retest_sess:
        # Check if student has completed a diagnostic session
        has_completed_diag = (
            db.query(AssessmentSession)
            .filter(
                AssessmentSession.student_id == student.id,
                AssessmentSession.kind == "diagnostic",
                AssessmentSession.status == "completed",
            )
            .first()
        )
        if has_completed_diag:
            retest_sess = AssessmentSession(
                id=f"sess_{uuid.uuid4().hex[:16]}",
                student_id=student.id,
                kind="retest",
                status="active",
                question_limit=10,
                answered_count=0,
                concept_id=id,
                consent=True,
                started_at=utcnow(),
            )
            db.add(retest_sess)
            db.commit()

    return LearningCompleteResponse(
        status="completed",
        concept_id=id,
        retest_enabled=True,
        retest_session_id=retest_sess.id if retest_sess else None,
    )


# --- 7. Historical Report (Section 11.12) ---

@router.get("/report", response_model=HistoricalReportResponse)
def get_historical_report(
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> HistoricalReportResponse:
    """Return historical learning report comparing epochs, retest outcomes, and trends."""
    graph = load_graph_from_db(db)
    topological_order = graph.get_topological_order()
    concepts_list = db.query(Concept).all()
    concepts_by_id = {c.id: c for c in concepts_list}

    # Replay mastery from db to reconstruct complete epoch history and outcomes
    replay_res = replay_student_mastery_from_db(db, student.id)

    mastery_list = (
        db.query(StudentConceptMastery)
        .filter(StudentConceptMastery.student_id == student.id)
        .all()
    )
    mastery_by_id = {m.concept_id: m for m in mastery_list}

    diag_service = DiagnosisService(db)
    diag_res = diag_service.compute_student_diagnosis(student_id=student.id)
    path_map = {item.concept_id: item for item in diag_res.learning_path}

    concept_reports: List[ConceptReportOut] = []
    for cid in topological_order:
        c_obj = concepts_by_id[cid]
        curr_state = replay_res.current_states.get(cid)
        history = replay_res.epoch_histories.get(cid, [])
        outcome_tuple = replay_res.retest_outcomes.get(cid, ("not_verified", True))
        trend = replay_res.trends.get(cid, "none")
        persistent_gap = replay_res.persistent_gaps.get(cid, False)

        m = mastery_by_id.get(cid)
        is_ready = m.ready if m else False
        path_item = path_map.get(cid)
        is_deferred = path_item.deferred if path_item else False

        epochs_out = [
            {
                "epoch_index": snap.epoch_index,
                "n_direct_answers": snap.n_direct_answers,
                "final_direct_estimate": snap.final_direct_estimate,
                "final_status": snap.final_status,
                "ready": snap.ready,
            }
            for snap in history
        ]
        # Include current epoch
        if curr_state:
            epochs_out.append({
                "epoch_index": curr_state.epoch_index,
                "n_direct_answers": curr_state.n_direct_questions,
                "final_direct_estimate": curr_state.direct_estimate,
                "final_status": curr_state.status,
                "ready": curr_state.ready,
            })

        concept_reports.append(
            ConceptReportOut(
                concept_id=cid,
                concept_name=c_obj.name,
                current_status=curr_state.status if curr_state else "unassessed",
                current_estimate=curr_state.direct_estimate if curr_state else 0.5,
                outcome=outcome_tuple[0],
                verification_limited=outcome_tuple[1],
                ready=is_ready,
                deferred=is_deferred,
                trend=trend,
                persistent_gap=persistent_gap,
                epochs=epochs_out,
            )
        )

    return HistoricalReportResponse(
        student_id=student.id,
        concepts=concept_reports,
    )
