"""Session endpoints for student assessments.

Conforms strictly to Specification v3.0 Sections 11.1 - 11.5.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as DBSession

from app.core.auth import get_current_student
from app.db.session import get_db
from app.models.session import Student
from app.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    InteractionEventRequest,
    InteractionEventResponse,
    NextQuestionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    SubmitSessionResponse,
)
from app.services.session_service import SessionService, utcnow

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    request: CreateSessionRequest,
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> CreateSessionResponse:
    """Create a new diagnostic, retest, or practice session (Section 11.1)."""
    service = SessionService(db)
    return service.create_session(
        student_id=student.id,
        kind=request.kind,
        consent=request.consent,
        concept_id=request.concept_id,
    )


@router.get("/{id}/next", response_model=NextQuestionResponse)
def get_next_question(
    id: str,
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> NextQuestionResponse:
    """Idempotently fetch current unanswered question or issue the next one (Section 11.2)."""
    service = SessionService(db)
    return service.get_or_issue_next_question(
        session_id=id,
        student_id=student.id,
    )


@router.post("/{id}/events", response_model=InteractionEventResponse)
def record_event(
    id: str,
    request: InteractionEventRequest,
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> InteractionEventResponse:
    """Record a fine-grained interaction event (Section 11.3)."""
    service = SessionService(db)
    event_id = service.record_interaction_event(
        session_id=id,
        student_id=student.id,
        event_type=request.event_type,
        payload=request.payload,
        question_id=request.question_id,
        client_timestamp=request.client_timestamp,
    )
    return InteractionEventResponse(
        event_id=event_id,
        session_id=id,
        event_type=request.event_type,
        server_timestamp=utcnow(),
    )


@router.post("/{id}/answers", response_model=SubmitAnswerResponse)
def submit_answer(
    id: str,
    request: SubmitAnswerRequest,
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> SubmitAnswerResponse:
    """Submit an answer to the currently issued question (Section 11.4)."""
    service = SessionService(db)
    return service.submit_answer(
        session_id=id,
        student_id=student.id,
        question_id=request.question_id,
        selected_option_id=request.selected_option_id,
        selected_option_key=request.selected_option_key,
        confidence=request.confidence,
        client_response_time_ms=request.client_response_time_ms,
        assisted=request.assisted,
        event_ids=request.event_ids,
    )


@router.post("/{id}/submit", response_model=SubmitSessionResponse)
def submit_session(
    id: str,
    student: Student = Depends(get_current_student),
    db: DBSession = Depends(get_db),
) -> SubmitSessionResponse:
    """Explicitly finalize an assessment session (Section 11.5)."""
    service = SessionService(db)
    return service.submit_session(
        session_id=id,
        student_id=student.id,
    )
