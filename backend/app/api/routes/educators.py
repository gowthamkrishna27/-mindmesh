"""Educator registration, self-management, analytics, and student drill-down routes.

Conforms to Specification v3.0 Sections 11.0, 19.2, 19.4, 19.5, 19.6, 19.8.
"""

from math import ceil
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.auth import AuthenticatedIdentity, get_current_identity, require_educator
from app.core.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import hash_password
from app.db.session import get_db
from app.models.auth import Class, Educator, EducatorClassAssignment, Section
from app.models.curriculum import Concept
from app.models.engine import StudentConceptMastery
from app.models.session import (
    DiagnosisSnapshot,
    LearningCompletion,
    Session as AssessmentSession,
    Student,
)
from app.schemas.auth import (
    EducatorAssignmentDetail,
    EducatorProfileResponse,
    EducatorRegisterRequest,
    EducatorResponse,
)
from app.schemas.educator_analytics import (
    ClassAnalyticsResponse,
    EducatorRootGapDetail,
    EducatorStudentDiagnosisResponse,
    EducatorStudentListItem,
    EducatorStudentProgressResponse,
    PaginatedStudentsResponse,
    StudentConceptProgressItem,
    StudentSessionSummary,
)
from app.services.analytics_service import calculate_class_analytics
from app.services.diagnosis_service import DiagnosisService
from app.services.graph import load_graph_from_db
from app.services.replay import replay_student_mastery_from_db
from app.services.scope_service import (
    get_authorized_student_query,
    verify_student_access,
)

router = APIRouter(prefix="/educators", tags=["Educators"])


@router.post("/register", response_model=EducatorResponse, status_code=status.HTTP_201_CREATED)
def register_educator(
    payload: EducatorRegisterRequest,
    db: Session = Depends(get_db),
) -> EducatorResponse:
    """Self-register an educator account.
    
    Always creates an account with status = 'pending'.
    Never accepts client-specified roles or approval states.
    Prevents duplicate emails and hashes passwords with bcrypt.
    """
    normalized_email = payload.email.strip().lower()

    # Prevent duplicate educator identities
    existing = db.query(Educator).filter(Educator.email == normalized_email).first()
    if existing:
        raise ConflictError(
            "An account with this email address already exists.",
            code="EMAIL_ALREADY_EXISTS",
        )

    hashed_pw = hash_password(payload.password)
    educator = Educator(
        email=normalized_email,
        password_hash=hashed_pw,
        display_name=payload.display_name.strip(),
        status="pending",
    )
    db.add(educator)
    db.commit()
    db.refresh(educator)
    return educator


@router.get("/me", response_model=EducatorProfileResponse)
def get_my_profile(
    identity: AuthenticatedIdentity = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> EducatorProfileResponse:
    """Return the authenticated educator's profile and current activation status."""
    if identity.role != "educator":
        raise ForbiddenError("Educator access required", code="FORBIDDEN")

    educator = db.query(Educator).filter(Educator.id == identity.id).first()
    if not educator:
        raise UnauthorizedError("Educator account not found", code="ACCOUNT_NOT_FOUND")

    return educator


@router.get("/me/assignments", response_model=List[EducatorAssignmentDetail])
def get_my_assignments(
    educator: Educator = Depends(require_educator),
    db: Session = Depends(get_db),
) -> List[EducatorAssignmentDetail]:
    """List active class and section assignments for the authenticated, approved educator.
    
    Pending, rejected, or suspended educators are denied access.
    """
    assignments = (
        db.query(EducatorClassAssignment)
        .filter(
            EducatorClassAssignment.educator_id == educator.id,
            EducatorClassAssignment.active.is_(True),
        )
        .order_by(EducatorClassAssignment.created_at.desc())
        .all()
    )

    results: List[EducatorAssignmentDetail] = []
    for a in assignments:
        target_class = db.query(Class).filter(Class.id == a.class_id).first()
        target_section = None
        if a.section_id:
            target_section = db.query(Section).filter(Section.id == a.section_id).first()

        results.append(
            EducatorAssignmentDetail(
                id=a.id,
                class_id=a.class_id,
                class_name=target_class.name if target_class else "Unknown",
                class_code=target_class.code if target_class else "UNKNOWN",
                section_id=a.section_id,
                section_name=target_section.name if target_section else None,
                section_code=target_section.code if target_section else None,
                active=a.active,
                created_at=a.created_at,
            )
        )

    return results


# --- Phase 7 Educator Analytics & Student Drill-Down Endpoints ---


@router.get("/me/classes/{class_id}/analytics", response_model=ClassAnalyticsResponse)
def get_class_analytics(
    class_id: str,
    section_id: Optional[str] = Query(None, description="Optional section filter within class"),
    educator: Educator = Depends(require_educator),
    db: Session = Depends(get_db),
) -> ClassAnalyticsResponse:
    """Return aggregate learning analytics for a class/section within educator's authorized scope.
    
    Enforces scope checks, explicit denominators, and heuristic disclaimers.
    """
    return calculate_class_analytics(
        educator_id=educator.id,
        class_id=class_id,
        section_id=section_id,
        db=db,
    )


@router.get("/me/students", response_model=PaginatedStudentsResponse)
def get_authorized_students(
    class_id: Optional[str] = Query(None, description="Narrow filter by class"),
    section_id: Optional[str] = Query(None, description="Narrow filter by section"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    educator: Educator = Depends(require_educator),
    db: Session = Depends(get_db),
) -> PaginatedStudentsResponse:
    """List students currently within the educator's assigned scope with validated pagination.
    
    Scope restrictions are applied in SQL directly. Query parameters can only narrow access.
    """
    query = get_authorized_student_query(
        educator_id=educator.id,
        class_id=class_id,
        section_id=section_id,
        db=db,
    )

    total = query.count()
    total_pages = ceil(total / page_size) if total > 0 else 0
    students: List[Student] = (
        query.order_by(Student.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Preload class and section mappings
    class_map = {c.id: c for c in db.query(Class).all()}
    section_map = {s.id: s for s in db.query(Section).all()}

    # Check which students have completed a diagnostic session
    student_ids = [s.id for s in students]
    completed_diag_student_ids = set()
    if student_ids:
        rows = (
            db.query(AssessmentSession.student_id)
            .filter(
                AssessmentSession.student_id.in_(student_ids),
                AssessmentSession.kind == "diagnostic",
                AssessmentSession.status == "completed",
            )
            .all()
        )
        completed_diag_student_ids = {r[0] for r in rows}

    items: List[EducatorStudentListItem] = []
    for s in students:
        c_obj = class_map.get(s.class_id) if s.class_id else None
        sec_obj = section_map.get(s.section_id) if s.section_id else None

        items.append(
            EducatorStudentListItem(
                id=s.id,
                name=s.name,
                email=s.email,
                class_id=s.class_id,
                class_name=c_obj.name if c_obj else None,
                class_code=c_obj.code if c_obj else None,
                section_id=s.section_id,
                section_name=sec_obj.name if sec_obj else None,
                section_code=sec_obj.code if sec_obj else None,
                has_completed_diagnostic=(s.id in completed_diag_student_ids),
                created_at=s.created_at,
            )
        )

    return PaginatedStudentsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/me/students/{student_id}/diagnosis", response_model=EducatorStudentDiagnosisResponse)
def get_student_diagnosis_drilldown(
    student_id: str,
    educator: Educator = Depends(require_educator),
    db: Session = Depends(get_db),
) -> EducatorStudentDiagnosisResponse:
    """Return an authorized student's latest finalized diagnosis and evidence.
    
    Active/unfinished sessions are rejected. Denies cross-class and cross-section access.
    """
    student = verify_student_access(
        educator_id=educator.id,
        student_id=student_id,
        db=db,
    )

    # Find student's latest finalized diagnostic session
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
        raise NotFoundError(
            "No finalized diagnostic assessment found for student. In-progress or unassessed sessions are not disclosed as diagnoses.",
            code="DIAGNOSIS_NOT_FOUND",
        )

    diag_service = DiagnosisService(db)
    diag_res = diag_service.compute_student_diagnosis(
        student_id=student.id,
        session_id=latest_completed.id,
    )

    root_gaps = [
        EducatorRootGapDetail(
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
            evidence_response_ids=rg.evidence_response_ids,
        )
        for rg in diag_res.root_gaps
    ]

    return EducatorStudentDiagnosisResponse(
        student_id=student.id,
        student_name=student.name,
        session_id=latest_completed.id,
        diagnosed_at=latest_completed.completed_at or latest_completed.created_at,
        root_gaps=root_gaps,
        weak_concepts=diag_res.weak_concepts,
        needs_more_evidence=diag_res.needs_more_evidence,
        learning_path_concepts=[item.concept_id for item in diag_res.learning_path],
        unlocked_concepts=diag_res.unlocked_concepts,
        rationale=diag_res.rationale,
    )


@router.get("/me/students/{student_id}/progress", response_model=EducatorStudentProgressResponse)
def get_student_progress_drilldown(
    student_id: str,
    educator: Educator = Depends(require_educator),
    db: Session = Depends(get_db),
) -> EducatorStudentProgressResponse:
    """Return an authorized student's learning progress, sessions history, and retest outcomes."""
    student = verify_student_access(
        educator_id=educator.id,
        student_id=student_id,
        db=db,
    )

    # 1. Sessions history
    sessions = (
        db.query(AssessmentSession)
        .filter(AssessmentSession.student_id == student.id)
        .order_by(AssessmentSession.started_at.desc())
        .all()
    )
    session_summaries = [
        StudentSessionSummary(
            session_id=s.id,
            kind=s.kind,
            status=s.status,
            answered_count=s.answered_count,
            started_at=s.started_at,
            completed_at=s.completed_at,
            completion_reason=s.completion_reason,
        )
        for s in sessions
    ]

    # 2. Concept progress via replay
    graph = load_graph_from_db(db)
    topological_order = graph.get_topological_order()
    concepts = db.query(Concept).all()
    concepts_by_id = {c.id: c.name for c in concepts}

    replay_res = replay_student_mastery_from_db(db, student.id)
    masteries = (
        db.query(StudentConceptMastery)
        .filter(StudentConceptMastery.student_id == student.id)
        .all()
    )
    mastery_by_id = {m.concept_id: m for m in masteries}

    # Learning completions
    completions = (
        db.query(LearningCompletion)
        .filter(LearningCompletion.student_id == student.id)
        .all()
    )
    completion_by_id = {c.concept_id: c.completed_at for c in completions}

    concepts_progress: List[StudentConceptProgressItem] = []
    for cid in topological_order:
        c_name = concepts_by_id.get(cid, cid)
        curr_state = replay_res.current_states.get(cid)
        outcome_tuple = replay_res.retest_outcomes.get(cid, ("not_verified", True))
        trend = replay_res.trends.get(cid, "none")
        persistent_gap = replay_res.persistent_gaps.get(cid, False)
        m = mastery_by_id.get(cid)
        is_ready = m.ready if m else False
        completed_at = completion_by_id.get(cid)

        concepts_progress.append(
            StudentConceptProgressItem(
                concept_id=cid,
                concept_name=c_name,
                current_status=curr_state.status if curr_state else "unassessed",
                current_estimate=curr_state.direct_estimate if curr_state else 0.5,
                ready=is_ready,
                retest_outcome=outcome_tuple[0],
                verification_limited=outcome_tuple[1],
                trend=trend,
                persistent_gap=persistent_gap,
                learning_completed=(completed_at is not None),
                learning_completed_at=completed_at,
            )
        )

    return EducatorStudentProgressResponse(
        student_id=student.id,
        student_name=student.name,
        class_id=student.class_id,
        section_id=student.section_id,
        sessions=session_summaries,
        concepts_progress=concepts_progress,
    )
