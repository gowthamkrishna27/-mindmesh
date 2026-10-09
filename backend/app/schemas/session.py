"""Pydantic schemas for student assessment sessions, events, and answers.

Conforms strictly to Specification v3.0 Sections 6, 8, 11.1 - 11.5.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Session Creation (Section 11.1) ---

class CreateSessionRequest(BaseModel):
    """Payload to create a new assessment session."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["diagnostic", "retest", "practice"]
    consent: bool
    concept_id: Optional[str] = Field(
        default=None,
        description="Required for practice sessions; concept being practiced.",
    )


class CreateSessionResponse(BaseModel):
    """Response returned upon session creation."""

    session_id: str
    kind: str
    status: str
    question_limit: int
    answered_count: int


# --- Question Issuance (Section 11.2) ---

class QuestionOptionPublic(BaseModel):
    """Option payload returned to the student.

    CRITICAL: Never expose correct_option_id, is_correct, or misconception mapping!
    """

    id: int
    option_key: str
    text: str


class QuestionPublic(BaseModel):
    """Question item payload returned to the student."""

    id: str
    primary_concept_id: str
    question_family: str
    difficulty: int
    expected_time_s: int
    prompt: str
    options: List[QuestionOptionPublic]
    confidence_options: List[str] = ["not_sure", "fairly_sure", "sure"]


class SessionProgress(BaseModel):
    """Progress metrics within the session."""

    answered_count: int
    question_limit: int


class NextQuestionResponse(BaseModel):
    """Response returned by GET /sessions/{id}/next."""

    session_id: str
    status: str
    question: Optional[QuestionPublic] = None
    progress: SessionProgress
    completion_reason: Optional[str] = None


# --- Interaction Events (Section 11.3) ---

class InteractionEventRequest(BaseModel):
    """Event payload recorded during question interaction."""

    model_config = ConfigDict(extra="forbid")

    event_type: str = Field(
        ...,
        description="Allowed: question_displayed, first_interaction, option_changed, hint_requested, submit_intent",
    )
    payload: Dict[str, Any] = Field(default_factory=dict)
    question_id: Optional[str] = None
    client_timestamp: Optional[datetime] = None


class InteractionEventResponse(BaseModel):
    """Response returned after recording an interaction event."""

    event_id: int
    session_id: str
    event_type: str
    server_timestamp: datetime


# --- Answer Submission (Section 11.4) ---

class SubmitAnswerRequest(BaseModel):
    """Answer submission payload."""

    model_config = ConfigDict(extra="forbid")

    question_id: str
    selected_option_id: Optional[int] = None
    selected_option_key: Optional[str] = None
    confidence: Literal["not_sure", "fairly_sure", "sure"]
    client_response_time_ms: Optional[int] = None
    assisted: Optional[bool] = False
    event_ids: Optional[List[int]] = None


class SubmitAnswerResponse(BaseModel):
    """Response returned after submitting an answer.

    CRITICAL: During diagnosis and retest, returns neutral progress only!
    Never reveals correctness or explanations.
    """

    session_id: str
    status: str
    progress: SessionProgress
    session_completed: bool


# --- Session Submission / Finalization (Section 11.5) ---

class SubmitSessionResponse(BaseModel):
    """Response returned upon submitting / completing a session."""

    session_id: str
    status: str
    completion_reason: str
    answered_count: int
    question_limit: int
