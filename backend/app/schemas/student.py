"""Pydantic schemas for student learning, graph, diagnosis, feedback, hints, and reports.

Conforms strictly to Specification v3.0 Sections 6, 7, 9, 10, 11.6 - 11.12.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Diagnosis (Section 11.6) ---

class RootGapOut(BaseModel):
    """Supported root gap details."""

    concept_id: str
    concept_name: str
    status: str
    estimate: float
    ready: bool
    blocker_score: float
    importance: float
    failed_dependents_explained: List[str]
    likely_cause: Optional[str]
    also_observed: List[str]
    signals_summary: Dict[str, Any]
    explanation: str
    recommended_action: str
    suggested_depth: str
    prerequisite_path: List[str]
    evidence_response_ids: List[int]
    evidence_question_ids: List[str]


class LearningPathItemOut(BaseModel):
    """Step on the recommended learning path."""

    concept_id: str
    concept_name: str
    kind: str  # fix_prerequisite, target, advance
    deferred: bool
    recommended_action: str
    suggested_depth: str


class DiagnosisResponse(BaseModel):
    """Response returned by GET /students/me/diagnosis."""

    student_id: str
    session_id: Optional[str]
    is_finalized: bool
    root_gaps: List[RootGapOut]
    weak_concepts: List[str]
    needs_more_evidence: List[str]
    learning_path: List[LearningPathItemOut]
    unlocked_concepts: List[str]
    rationale: str


# --- Graph (Section 11.7) ---

class GraphNodeOut(BaseModel):
    """Concept node in student learning graph."""

    id: str
    name: str
    branch: str
    visual_status: str  # mastered, needs_attention, uncertain, unassessed
    backend_status: str  # mastered, confirmed_gap, suspected_gap, uncertain, unassessed
    mastery_estimate: float
    direct_estimate: float
    direct_count: int
    uncertainty_flag: bool
    short_reason: str
    on_path: bool
    ready: bool
    unlocked: bool
    likely_cause: Optional[str]
    trend: str


class GraphEdgeOut(BaseModel):
    """Directed edge in learning graph (prerequisite -> dependent)."""

    from_concept_id: str
    to_concept_id: str


class GraphResponse(BaseModel):
    """Response returned by GET /students/me/graph."""

    nodes: List[GraphNodeOut]
    edges: List[GraphEdgeOut]


# --- Concept Detail (Section 11.8) ---

class ResourceItemOut(BaseModel):
    """Curated learning resource at a specific depth."""

    depth: str
    title: str
    summary: str
    content: str


class ConceptDetailResponse(BaseModel):
    """Response returned by GET /students/me/concepts/{id}."""

    id: str
    name: str
    description: str
    learning_objective: str
    branch: str
    visual_status: str
    backend_status: str
    estimate: float
    direct_estimate: float
    ready: bool
    evidence_response_ids: List[int]
    reason_tags: List[Dict[str, Any]]
    likely_cause: Optional[str]
    attempt_history: Dict[str, Any]
    reason_text: str
    prerequisites: List[str]
    dependents: List[str]
    resources: Dict[str, ResourceItemOut]
    suggested_depth: str
    next_action: str


# --- Feedback (Section 11.9) ---

class QuestionFeedbackOut(BaseModel):
    """Post-test question disclosure feedback."""

    question_id: str
    concept_id: str
    concept_name: str
    prompt: str
    selected_option_key: str
    is_correct: bool
    correct_option_key: str
    explanation: str
    likely_cause: Optional[str]
    reason_tags: List[str]


class FeedbackResponse(BaseModel):
    """Response returned by GET /students/me/feedback."""

    session_id: str
    completed_at: Optional[str]
    rationale: str
    root_gaps: List[RootGapOut]
    questions_feedback: List[QuestionFeedbackOut]


# --- Progressive Hints (Section 11.10) ---

class HintRequest(BaseModel):
    """Payload to request progressive hint."""

    model_config = ConfigDict(extra="forbid")

    question_id: str
    requested_level: Literal[1, 2] = Field(..., description="1 = nudge, 2 = conceptual clue")


class HintResponse(BaseModel):
    """Response returned by POST /students/me/concepts/{id}/hints."""

    question_id: str
    concept_id: str
    hint_level: int
    content: str


# --- Learning Complete (Section 11.11) ---

class LearningCompleteResponse(BaseModel):
    """Response returned by POST /students/me/learning/{id}/complete."""

    status: str
    concept_id: str
    retest_enabled: bool
    retest_session_id: Optional[str] = None


# --- Historical Report (Section 11.12) ---

class ConceptReportOut(BaseModel):
    """Historical learning report for a concept."""

    concept_id: str
    concept_name: str
    current_status: str
    current_estimate: float
    outcome: str  # recovered, improving, no_change, declined, not_verified
    verification_limited: bool
    ready: bool
    deferred: bool
    trend: str
    persistent_gap: bool
    epochs: List[Dict[str, Any]]


class HistoricalReportResponse(BaseModel):
    """Response returned by GET /students/me/report."""

    student_id: str
    concepts: List[ConceptReportOut]
