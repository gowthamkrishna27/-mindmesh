"""Assessment session lifecycle, event recording, and answer submission service.

Conforms strictly to Specification v3.0 Sections 6, 7, 8, 11.1 - 11.5, 12, 13.
"""

from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.settings_rules import MAX_DIAGNOSTIC_SESSION_QUESTIONS
from app.models.curriculum import Concept, Question, QuestionOption
from app.models.engine import (
    ConceptEpoch,
    Response,
    ResponseEvidence,
    StudentConceptMastery,
)
from app.models.session import (
    DiagnosisSnapshot,
    InteractionEvent,
    SelectionLog,
    Session,
    SessionQuestionIssue,
    Student,
)
from app.schemas.session import (
    CreateSessionResponse,
    NextQuestionResponse,
    QuestionOptionPublic,
    QuestionPublic,
    SessionProgress,
    SubmitAnswerResponse,
    SubmitSessionResponse,
)
from app.services.evidence import (
    calculate_response_weight,
    derive_reason_tags,
    generate_evidence_items,
)
from app.services.graph import GraphService, load_graph_from_db
from app.services.mastery import ConceptMasteryState, apply_evidence_item
from app.services.question_selector import QuestionSelector
from app.services.signals import derive_signals


ALLOWED_EVENT_TYPES = {
    "question_displayed",
    "first_interaction",
    "option_changed",
    "hint_requested",
    "submit_intent",
}

MAX_EVENT_PAYLOAD_BYTES = 4096


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SessionService:
    """Manages session creation, question issuance, event tracking, and answer submission."""

    def __init__(self, db: DBSession):
        self.db = db
        self.graph_service: GraphService = load_graph_from_db(db)
        self.selector = QuestionSelector(db=db, graph_service=self.graph_service)

    # --- 1. Session Creation (Section 11.1) ---

    def create_session(
        self,
        student_id: str,
        kind: str,
        consent: bool,
        concept_id: Optional[str] = None,
    ) -> CreateSessionResponse:
        """Create a new diagnostic, retest, or practice assessment session."""
        # 1. Enforce consent (Section 6.1, 11.1)
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "CONSENT_REQUIRED",
                    "message": "Explicit consent is required to start an assessment session.",
                },
            )

        # Update student consent if not already recorded
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            student = Student(id=student_id, consent_given=True, consent_given_at=utcnow())
            self.db.add(student)
        elif not student.consent_given:
            student.consent_given = True
            student.consent_given_at = utcnow()

        # 2. Validate kind-specific rules
        if kind == "retest":
            # Retest requires an existing completed diagnostic session for this student
            completed_diag = (
                self.db.query(Session)
                .filter(
                    Session.student_id == student_id,
                    Session.kind == "diagnostic",
                    Session.status == "completed",
                )
                .first()
            )
            if not completed_diag:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "COMPLETED_DIAGNOSTIC_REQUIRED",
                        "message": "Retest session requires an existing completed diagnostic session.",
                    },
                )
        elif kind == "practice":
            if not concept_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "CONCEPT_ID_REQUIRED",
                        "message": "Practice session requires a target concept_id.",
                    },
                )
            concept_exists = self.db.query(Concept).filter(Concept.id == concept_id).first()
            if not concept_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "CONCEPT_NOT_FOUND",
                        "message": f"Concept '{concept_id}' not found in curriculum.",
                    },
                )

        session_id = f"sess_{uuid.uuid4().hex[:16]}"
        question_limit = MAX_DIAGNOSTIC_SESSION_QUESTIONS if kind == "diagnostic" else 10

        new_session = Session(
            id=session_id,
            student_id=student_id,
            kind=kind,
            status="active",
            question_limit=question_limit,
            answered_count=0,
            concept_id=concept_id,
            consent=consent,
            started_at=utcnow(),
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)

        return CreateSessionResponse(
            session_id=new_session.id,
            kind=new_session.kind,
            status=new_session.status,
            question_limit=new_session.question_limit,
            answered_count=new_session.answered_count,
        )

    # --- 2. Question Issuance (Section 11.2) ---

    def get_or_issue_next_question(
        self,
        session_id: str,
        student_id: str,
    ) -> NextQuestionResponse:
        """Idempotently retrieve current unanswered question or issue the next one."""
        session = self._get_session_for_student(session_id, student_id)

        # If session is already completed, return status
        if session.status == "completed":
            return NextQuestionResponse(
                session_id=session.id,
                status=session.status,
                question=None,
                progress=SessionProgress(
                    answered_count=session.answered_count,
                    question_limit=session.question_limit,
                ),
                completion_reason=session.completion_reason,
            )

        # 1. Idempotency check: is there an issued, unanswered question?
        unanswered_issue = (
            self.db.query(SessionQuestionIssue)
            .filter(
                SessionQuestionIssue.session_id == session_id,
                SessionQuestionIssue.status == "issued",
            )
            .first()
        )
        if unanswered_issue:
            question = self.db.query(Question).filter(Question.id == unanswered_issue.question_id).first()
            if question:
                return NextQuestionResponse(
                    session_id=session.id,
                    status=session.status,
                    question=self._to_public_question(question),
                    progress=SessionProgress(
                        answered_count=session.answered_count,
                        question_limit=session.question_limit,
                    ),
                )

        # 2. Check if question limit has been reached
        if session.answered_count >= session.question_limit:
            self._finalize_session(session, completion_reason="question_limit_reached")
            return NextQuestionResponse(
                session_id=session.id,
                status="completed",
                question=None,
                progress=SessionProgress(
                    answered_count=session.answered_count,
                    question_limit=session.question_limit,
                ),
                completion_reason="question_limit_reached",
            )

        # 3. Select next question adaptively
        selection = self.selector.select_next_diagnostic_question(
            session_id=session_id,
            student_id=student_id,
        )

        if selection.exhausted or not selection.question:
            completion_reason = (
                "question_bank_exhausted"
                if selection.reason == "question_bank_exhausted"
                else "question_limit_reached"
            )
            self._finalize_session(session, completion_reason=completion_reason)
            return NextQuestionResponse(
                session_id=session.id,
                status="completed",
                question=None,
                progress=SessionProgress(
                    answered_count=session.answered_count,
                    question_limit=session.question_limit,
                ),
                completion_reason=completion_reason,
            )

        winning_q = selection.question

        # 4. Record SelectionLog and SessionQuestionIssue
        log_entry = SelectionLog(
            session_id=session_id,
            question_id=winning_q.id,
            candidate_scores=selection.candidate_scores,
            reason=selection.reason,
            created_at=utcnow(),
        )
        self.db.add(log_entry)

        new_issue = SessionQuestionIssue(
            session_id=session_id,
            question_id=winning_q.id,
            issued_at=utcnow(),
            status="issued",
        )
        self.db.add(new_issue)
        self.db.commit()

        return NextQuestionResponse(
            session_id=session.id,
            status=session.status,
            question=self._to_public_question(winning_q),
            progress=SessionProgress(
                answered_count=session.answered_count,
                question_limit=session.question_limit,
            ),
        )

    # --- 3. Interaction Events (Section 11.3) ---

    def record_interaction_event(
        self,
        session_id: str,
        student_id: str,
        event_type: str,
        payload: Dict[str, Any],
        question_id: Optional[str] = None,
        client_timestamp: Optional[datetime] = None,
    ) -> int:
        """Record a validated interaction event associated with the currently issued question."""
        session = self._get_session_for_student(session_id, student_id)
        if session.status != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "SESSION_NOT_ACTIVE",
                    "message": f"Cannot record events for {session.status} session.",
                },
            )

        # Validate event type
        if event_type not in ALLOWED_EVENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_EVENT_TYPE",
                    "message": f"Event type '{event_type}' not allowed.",
                },
            )

        # Payload size limit check
        import json
        payload_str = json.dumps(payload)
        if len(payload_str.encode("utf-8")) > MAX_EVENT_PAYLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "PAYLOAD_TOO_LARGE",
                    "message": f"Event payload exceeds maximum {MAX_EVENT_PAYLOAD_BYTES} bytes limit.",
                },
            )

        # Find currently issued unanswered question
        active_issue = (
            self.db.query(SessionQuestionIssue)
            .filter(
                SessionQuestionIssue.session_id == session_id,
                SessionQuestionIssue.status == "issued",
            )
            .first()
        )
        if not active_issue:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "NO_ACTIVE_QUESTION",
                    "message": "No unanswered question is currently issued for this session.",
                },
            )

        if question_id and question_id != active_issue.question_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "QUESTION_MISMATCH",
                    "message": f"Event question_id '{question_id}' does not match issued '{active_issue.question_id}'.",
                },
            )

        # Persist event with server timestamp
        event = InteractionEvent(
            session_id=session_id,
            question_id=active_issue.question_id,
            event_type=event_type,
            payload=payload,
            server_timestamp=utcnow(),
            client_timestamp=client_timestamp,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event.id

    # --- 4. Answer Submission (Section 11.4) ---

    def submit_answer(
        self,
        session_id: str,
        student_id: str,
        question_id: str,
        selected_option_id: Optional[int] = None,
        selected_option_key: Optional[str] = None,
        confidence: str = "fairly_sure",
        client_response_time_ms: Optional[int] = None,
        assisted: Optional[bool] = False,
        event_ids: Optional[List[int]] = None,
    ) -> SubmitAnswerResponse:
        """Process and persist an answer submission in an atomic database transaction."""
        session = self._get_session_for_student(session_id, student_id)
        if session.status != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "SESSION_NOT_ACTIVE",
                    "message": f"Cannot submit answers to a {session.status} session.",
                },
            )

        # Verify question is currently issued to this session
        active_issue = (
            self.db.query(SessionQuestionIssue)
            .filter(
                SessionQuestionIssue.session_id == session_id,
                SessionQuestionIssue.question_id == question_id,
                SessionQuestionIssue.status == "issued",
            )
            .first()
        )
        if not active_issue:
            # Check if duplicate answer
            existing_resp = (
                self.db.query(Response)
                .filter(
                    Response.session_id == session_id,
                    Response.question_id == question_id,
                )
                .first()
            )
            if existing_resp:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "DUPLICATE_ANSWER",
                        "message": f"Question '{question_id}' has already been answered in this session.",
                    },
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "QUESTION_NOT_ISSUED",
                    "message": f"Question '{question_id}' is not currently issued for this session.",
                },
            )

        # Load question and options
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "QUESTION_NOT_FOUND", "message": f"Question '{question_id}' not found."},
            )

        # Resolve selected option
        options_list = (
            self.db.query(QuestionOption)
            .filter(QuestionOption.question_id == question_id)
            .all()
        )
        selected_opt: Optional[QuestionOption] = None
        correct_opt: Optional[QuestionOption] = None

        for opt in options_list:
            if opt.is_correct:
                correct_opt = opt
            if selected_option_id is not None and opt.id == selected_option_id:
                selected_opt = opt
            elif selected_option_key is not None and opt.option_key.upper() == selected_option_key.upper():
                selected_opt = opt

        if not selected_opt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_OPTION",
                    "message": "Selected option does not belong to this question.",
                },
            )

        correct_option_key = correct_opt.option_key if correct_opt else ""
        is_correct = bool(selected_opt.is_correct)

        # Fetch stored interaction events for this question issue
        stored_events_query = (
            self.db.query(InteractionEvent)
            .filter(
                InteractionEvent.session_id == session_id,
                InteractionEvent.question_id == question_id,
            )
            .order_by(InteractionEvent.server_timestamp.asc())
            .all()
        )
        stored_events_data = [
            {
                "event_type": ev.event_type,
                "payload": ev.payload,
                "server_timestamp": ev.server_timestamp,
            }
            for ev in stored_events_query
        ]

        # Verify assistance: client cannot declare False if hints were requested
        has_hint_event = any(ev["event_type"] == "hint_requested" for ev in stored_events_data)
        is_assisted = bool(assisted or has_hint_event)

        # Derive 7.1 signals using server clock
        answered_at = utcnow()
        signals = derive_signals(
            issued_at=active_issue.issued_at,
            answered_at=answered_at,
            expected_time_s=question.expected_time_s,
            events=stored_events_data,
            selected_option_key=selected_opt.option_key,
            correct_option_key=correct_option_key,
            client_response_time_ms=client_response_time_ms,
        )

        # Calculate weight and reason tags
        weight = calculate_response_weight(
            is_correct=is_correct,
            confidence=confidence,
            signals=signals,
            assisted=is_assisted,
        )

        selected_opt_dict = {
            "maps_to_concept_id": selected_opt.maps_to_concept_id,
            "misconception_code": selected_opt.misconception_code,
        }
        reason_tags = derive_reason_tags(
            is_correct=is_correct,
            confidence=confidence,
            signals=signals,
            selected_option_data=selected_opt_dict,
        )

        # Generate evidence items
        direct_prereqs = self.graph_service.get_direct_prerequisites(question.primary_concept_id)
        evidence_items = generate_evidence_items(
            primary_concept_id=question.primary_concept_id,
            is_correct=is_correct,
            weight=weight,
            direct_prerequisites=direct_prereqs,
            selected_option_data=selected_opt_dict,
        )

        # Transactional write: response, evidence, mastery, issue status, session counts
        try:
            # 1. Create Response record
            response_rec = Response(
                student_id=student_id,
                session_id=session_id,
                question_id=question_id,
                selected_option_key=selected_opt.option_key,
                confidence=confidence,
                is_correct=is_correct,
                attempt_number=1,
                assisted=is_assisted,
                client_response_time_ms=client_response_time_ms,
                response_time_ms=signals.response_time_ms,
                time_class=signals.time_class,
                option_changes=signals.option_changes,
                first_selected_option_id=signals.first_selected_option_id,
                switched_from_correct=signals.switched_from_correct,
                signals_incomplete=signals.signals_incomplete,
                reason_tags=reason_tags,
                created_at=answered_at,
            )
            self.db.add(response_rec)
            self.db.flush()  # Populates response_rec.id

            # 2. Apply evidence to StudentConceptMastery and create ResponseEvidence rows
            affected_concepts = {item.concept_id for item in evidence_items}
            mastery_map: Dict[str, StudentConceptMastery] = {}
            for cid in affected_concepts:
                m_rec = (
                    self.db.query(StudentConceptMastery)
                    .filter(
                        StudentConceptMastery.student_id == student_id,
                        StudentConceptMastery.concept_id == cid,
                    )
                    .first()
                )
                if not m_rec:
                    m_rec = StudentConceptMastery(
                        student_id=student_id,
                        concept_id=cid,
                        epoch_index=0,
                        weighted_correct=1.0,
                        weighted_incorrect=1.0,
                        direct_weighted_correct=1.0,
                        direct_weighted_incorrect=1.0,
                        mastery_estimate=0.5,
                        direct_estimate=0.5,
                        status="unassessed",
                        ready=False,
                    )
                    self.db.add(m_rec)
                    self.db.flush()
                mastery_map[cid] = m_rec

            for ev_item in evidence_items:
                cid = ev_item.concept_id
                m_rec = mastery_map[cid]

                # Convert ORM mastery to ConceptMasteryState
                state = ConceptMasteryState(
                    concept_id=cid,
                    epoch_index=m_rec.epoch_index,
                    weighted_correct=m_rec.weighted_correct,
                    weighted_incorrect=m_rec.weighted_incorrect,
                    direct_weighted_correct=m_rec.direct_weighted_correct,
                    direct_weighted_incorrect=m_rec.direct_weighted_incorrect,
                    n_direct_questions=m_rec.n_direct_questions,
                    n_direct_correct=m_rec.n_direct_correct,
                    n_direct_incorrect=m_rec.n_direct_incorrect,
                    n_direct_unassisted=m_rec.n_direct_unassisted,
                    n_direct_correct_unassisted=m_rec.n_direct_correct_unassisted,
                    n_direct_primary=m_rec.n_direct_primary,
                    n_direct_mapped=m_rec.n_direct_mapped,
                    n_indirect=m_rec.n_indirect,
                )

                apply_evidence_item(
                    state=state,
                    item=ev_item,
                    is_assisted=is_assisted,
                    is_repeat=False,
                )

                # Write back state to ORM
                m_rec.weighted_correct = state.weighted_correct
                m_rec.weighted_incorrect = state.weighted_incorrect
                m_rec.direct_weighted_correct = state.direct_weighted_correct
                m_rec.direct_weighted_incorrect = state.direct_weighted_incorrect
                m_rec.n_direct_questions = state.n_direct_questions
                m_rec.n_direct_correct = state.n_direct_correct
                m_rec.n_direct_incorrect = state.n_direct_incorrect
                m_rec.n_direct_unassisted = state.n_direct_unassisted
                m_rec.n_direct_correct_unassisted = state.n_direct_correct_unassisted
                m_rec.n_direct_primary = state.n_direct_primary
                m_rec.n_direct_mapped = state.n_direct_mapped
                m_rec.n_indirect = state.n_indirect
                m_rec.mastery_estimate = state.mastery_estimate
                m_rec.direct_estimate = state.direct_estimate
                m_rec.status = state.status
                m_rec.ready = state.ready

                # Insert ResponseEvidence row
                ev_row = ResponseEvidence(
                    response_id=response_rec.id,
                    student_id=student_id,
                    concept_id=cid,
                    evidence_type=ev_item.evidence_type,
                    direction=ev_item.direction,
                    weight=ev_item.weight,
                    epoch_index=m_rec.epoch_index,
                    source_concept_id=ev_item.source_concept_id,
                    edge_prerequisite_id=ev_item.edge_prerequisite_id,
                    edge_dependent_id=ev_item.edge_dependent_id,
                    created_at=answered_at,
                )
                self.db.add(ev_row)

            # 3. Mark SessionQuestionIssue answered
            active_issue.status = "answered"

            # 4. Increment session answered count
            session.answered_count += 1

            # 5. Check if session limit reached
            if session.answered_count >= session.question_limit:
                self._finalize_session(session, completion_reason="question_limit_reached")

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        return SubmitAnswerResponse(
            session_id=session.id,
            status=session.status,
            progress=SessionProgress(
                answered_count=session.answered_count,
                question_limit=session.question_limit,
            ),
            session_completed=(session.status == "completed"),
        )

    # --- 5. Session Finalization (Section 11.5) ---

    def submit_session(
        self,
        session_id: str,
        student_id: str,
    ) -> SubmitSessionResponse:
        """Submit and finalize an assessment session early or explicitly."""
        session = self._get_session_for_student(session_id, student_id)
        if session.status == "completed":
            return SubmitSessionResponse(
                session_id=session.id,
                status=session.status,
                completion_reason=session.completion_reason or "completed",
                answered_count=session.answered_count,
                question_limit=session.question_limit,
            )

        self._finalize_session(session, completion_reason="early_submit")
        self.db.commit()

        return SubmitSessionResponse(
            session_id=session.id,
            status=session.status,
            completion_reason=session.completion_reason or "early_submit",
            answered_count=session.answered_count,
            question_limit=session.question_limit,
        )

    # --- Helper methods ---

    def _get_session_for_student(self, session_id: str, student_id: str) -> Session:
        session = self.db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "SESSION_NOT_FOUND", "message": f"Session '{session_id}' not found."},
            )
        if session.student_id != student_id:
            # Mask existence across students (Section 11.0, 11.13)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "SESSION_NOT_FOUND", "message": f"Session '{session_id}' not found."},
            )
        return session

    def _finalize_session(self, session: Session, completion_reason: str) -> None:
        """Mark session completed and record minimal diagnostic snapshots."""
        session.status = "completed"
        session.completion_reason = completion_reason
        session.completed_at = utcnow()

        # Generate minimal snapshots for all curriculum concepts
        all_concept_ids = list(self.graph_service.graph.nodes)
        existing_mastery = (
            self.db.query(StudentConceptMastery)
            .filter(StudentConceptMastery.student_id == session.student_id)
            .all()
        )
        mastery_by_cid = {m.concept_id: m for m in existing_mastery}

        for cid in all_concept_ids:
            # Check if snapshot already exists
            existing_snap = (
                self.db.query(DiagnosisSnapshot)
                .filter(
                    DiagnosisSnapshot.session_id == session.id,
                    DiagnosisSnapshot.concept_id == cid,
                )
                .first()
            )
            if existing_snap:
                continue

            m = mastery_by_cid.get(cid)
            snap = DiagnosisSnapshot(
                student_id=session.student_id,
                session_id=session.id,
                concept_id=cid,
                epoch_index=m.epoch_index if m else 0,
                mastery_estimate=m.mastery_estimate if m else 0.5,
                direct_estimate=m.direct_estimate if m else 0.5,
                status=m.status if m else "unassessed",
                ready=m.ready if m else False,
                likely_cause=None,
                also_observed=[],
                recommended_action=None,
                suggested_depth=None,
                created_at=utcnow(),
            )
            self.db.add(snap)

    def _to_public_question(self, question: Question) -> QuestionPublic:
        """Convert ORM Question to public API model without answer-key leakage."""
        options_out = [
            QuestionOptionPublic(
                id=opt.id,
                option_key=opt.option_key,
                text=opt.text,
            )
            for opt in question.options
        ]
        options_out.sort(key=lambda o: o.option_key)

        return QuestionPublic(
            id=question.id,
            primary_concept_id=question.primary_concept_id,
            question_family=question.question_family,
            difficulty=question.difficulty,
            expected_time_s=question.expected_time_s,
            prompt=question.prompt,
            options=options_out,
            confidence_options=["not_sure", "fairly_sure", "sure"],
        )
