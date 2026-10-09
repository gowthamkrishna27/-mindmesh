"""Pydantic schemas for Educator Analytics and Student Drill-down.

Conforms to Specification v3.0 Sections 19.4, 19.5, 19.8.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ConceptStatusDistribution(BaseModel):
    concept_id: str
    concept_name: str
    mastered: int = 0
    confirmed_gap: int = 0
    suspected_gap: int = 0
    uncertain: int = 0
    unassessed: int = 0
    mastered_rate: float = 0.0
    confirmed_gap_rate: float = 0.0
    suspected_gap_rate: float = 0.0
    uncertain_rate: float = 0.0


class AverageMasteryEstimate(BaseModel):
    concept_id: str
    concept_name: str
    average_mastery_estimate: float = 0.5
    average_direct_estimate: float = 0.5
    assessed_count: int = 0


class RootGapFrequencyItem(BaseModel):
    concept_id: str
    concept_name: str
    count: int
    percentage_of_assessed: float


class RetestOutcomesAggregate(BaseModel):
    recovered: int = 0
    improving: int = 0
    no_change: int = 0
    declined: int = 0
    not_verified: int = 0
    total_retests: int = 0


class ClassAnalyticsResponse(BaseModel):
    class_id: str
    class_name: str
    class_code: str
    section_id: Optional[str] = None
    section_name: Optional[str] = None
    section_code: Optional[str] = None
    total_students: int
    assessed_students: int
    diagnostic_completion_rate: float
    denominator_description: str
    concepts_status_distribution: List[ConceptStatusDistribution]
    average_mastery_estimates: List[AverageMasteryEstimate]
    common_root_gaps: List[RootGapFrequencyItem]
    retest_outcomes: RetestOutcomesAggregate
    heuristic_disclaimer: str = (
        "Estimates and status distributions represent rule-based heuristic "
        "evidence indicators and must not be interpreted as calibrated statistical probabilities."
    )


class EducatorStudentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: Optional[str] = None
    class_id: Optional[str] = None
    class_name: Optional[str] = None
    class_code: Optional[str] = None
    section_id: Optional[str] = None
    section_name: Optional[str] = None
    section_code: Optional[str] = None
    has_completed_diagnostic: bool
    created_at: datetime


class PaginatedStudentsResponse(BaseModel):
    items: List[EducatorStudentListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class EducatorRootGapDetail(BaseModel):
    concept_id: str
    concept_name: str
    status: str
    estimate: float
    ready: bool
    blocker_score: float
    importance: float
    failed_dependents_explained: List[str]
    likely_cause: Optional[str] = None
    also_observed: List[str] = []
    signals_summary: Dict[str, Any] = {}
    explanation: str
    recommended_action: str
    suggested_depth: str
    evidence_response_ids: List[int] = []


class EducatorStudentDiagnosisResponse(BaseModel):
    student_id: str
    student_name: str
    session_id: str
    diagnosed_at: datetime
    root_gaps: List[EducatorRootGapDetail]
    weak_concepts: List[str]
    needs_more_evidence: List[str]
    learning_path_concepts: List[str]
    unlocked_concepts: List[str]
    rationale: str


class StudentSessionSummary(BaseModel):
    session_id: str
    kind: str
    status: str
    answered_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    completion_reason: Optional[str] = None


class StudentConceptProgressItem(BaseModel):
    concept_id: str
    concept_name: str
    current_status: str
    current_estimate: float
    ready: bool
    retest_outcome: str
    verification_limited: bool
    trend: str
    persistent_gap: bool
    learning_completed: bool
    learning_completed_at: Optional[datetime] = None


class EducatorStudentProgressResponse(BaseModel):
    student_id: str
    student_name: str
    class_id: Optional[str] = None
    section_id: Optional[str] = None
    sessions: List[StudentSessionSummary]
    concepts_progress: List[StudentConceptProgressItem]
