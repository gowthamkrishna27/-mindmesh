"""Educator Analytics Service for MindMesh.

Conforms to Specification v3.0 Sections 19.4, 19.5, 19.6, 19.8:
- Backend-enforced scope authorization.
- Explicit denominators excluding unassessed students from failure rates.
- Heuristic mastery estimate disclaimers (not calibrated probabilities).
"""

from collections import Counter, defaultdict
from typing import Dict, List, Optional
from sqlalchemy.orm import Session as DBSession
from app.core.errors import ForbiddenError, NotFoundError
from app.models.auth import Class, EducatorClassAssignment, Section
from app.models.curriculum import Concept
from app.models.session import DiagnosisSnapshot, Session as AssessmentSession, Student
from app.schemas.educator_analytics import (
    AverageMasteryEstimate,
    ClassAnalyticsResponse,
    ConceptStatusDistribution,
    RetestOutcomesAggregate,
    RootGapFrequencyItem,
)
from app.services.diagnosis_service import DiagnosisService
from app.services.graph import load_graph_from_db
from app.services.replay import replay_student_mastery_from_db
from app.services.scope_service import (
    get_authorized_student_query,
    verify_educator_scope,
)


def calculate_class_analytics(
    educator_id: str,
    class_id: str,
    section_id: Optional[str] = None,
    db: DBSession = None,
) -> ClassAnalyticsResponse:
    """Calculate aggregate learning analytics for authorized students in a class/section."""
    # 1. Enforce backend scope authorization
    has_access = verify_educator_scope(
        educator_id=educator_id,
        class_id=class_id,
        section_id=section_id,
        db=db,
    )
    if not has_access:
        raise ForbiddenError(
            "Access to requested class and section scope is forbidden",
            code="SCOPE_UNAUTHORIZED",
        )

    # 2. Retrieve class and section entities
    target_class = db.query(Class).filter(Class.id == class_id).first()
    if not target_class:
        raise NotFoundError("Class not found", code="CLASS_NOT_FOUND")

    target_section = None
    if section_id:
        target_section = db.query(Section).filter(Section.id == section_id).first()
        if not target_section or target_section.class_id != class_id:
            raise NotFoundError("Section not found in class", code="SECTION_NOT_FOUND")

    # 3. Retrieve authorized student cohort directly via backend-scoped query
    student_query = get_authorized_student_query(
        educator_id=educator_id,
        class_id=class_id,
        section_id=section_id,
        db=db,
    )
    students: List[Student] = student_query.all()
    total_students = len(students)

    # 4. Resolve concepts in topological order
    graph = load_graph_from_db(db)
    topological_order = graph.get_topological_order()
    concepts = db.query(Concept).all()
    concepts_by_id = {c.id: c.name for c in concepts}

    if total_students == 0:
        return _empty_analytics_response(
            target_class=target_class,
            target_section=target_section,
            topological_order=topological_order,
            concepts_by_id=concepts_by_id,
        )

    student_ids = [s.id for s in students]

    # 5. Find latest completed diagnostic session per student
    completed_sessions = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.student_id.in_(student_ids),
            AssessmentSession.kind == "diagnostic",
            AssessmentSession.status == "completed",
        )
        .order_by(AssessmentSession.completed_at.desc())
        .all()
    )

    # Map latest session id per student
    latest_session_ids_by_student: Dict[str, str] = {}
    for sess in completed_sessions:
        if sess.student_id not in latest_session_ids_by_student:
            latest_session_ids_by_student[sess.student_id] = sess.id

    assessed_students = len(latest_session_ids_by_student)
    completion_rate = round(assessed_students / total_students, 4) if total_students > 0 else 0.0
    latest_session_ids = list(latest_session_ids_by_student.values())

    # 6. Retrieve latest diagnosis snapshots for assessed students
    snapshots: List[DiagnosisSnapshot] = []
    if latest_session_ids:
        snapshots = (
            db.query(DiagnosisSnapshot)
            .filter(DiagnosisSnapshot.session_id.in_(latest_session_ids))
            .all()
        )

    # Group snapshots by concept
    snapshots_by_concept: Dict[str, List[DiagnosisSnapshot]] = defaultdict(list)
    for snap in snapshots:
        snapshots_by_concept[snap.concept_id].append(snap)

    # 7. Concept status distribution and average mastery estimates
    status_distributions: List[ConceptStatusDistribution] = []
    average_mastery_list: List[AverageMasteryEstimate] = []

    for cid in topological_order:
        c_name = concepts_by_id.get(cid, cid)
        c_snaps = snapshots_by_concept.get(cid, [])
        status_counts = Counter([s.status for s in c_snaps])

        mastered = status_counts.get("mastered", 0)
        confirmed_gap = status_counts.get("confirmed_gap", 0)
        suspected_gap = status_counts.get("suspected_gap", 0)
        uncertain = status_counts.get("uncertain", 0)
        # Unassessed is assessed students with no snapshot or explicit unassessed
        unassessed = assessed_students - (mastered + confirmed_gap + suspected_gap + uncertain)
        if unassessed < 0:
            unassessed = 0

        # Rates are calculated strictly using assessed_students denominator
        den = assessed_students if assessed_students > 0 else 1
        dist = ConceptStatusDistribution(
            concept_id=cid,
            concept_name=c_name,
            mastered=mastered,
            confirmed_gap=confirmed_gap,
            suspected_gap=suspected_gap,
            uncertain=uncertain,
            unassessed=unassessed,
            mastered_rate=round(mastered / den, 4) if assessed_students > 0 else 0.0,
            confirmed_gap_rate=round(confirmed_gap / den, 4) if assessed_students > 0 else 0.0,
            suspected_gap_rate=round(suspected_gap / den, 4) if assessed_students > 0 else 0.0,
            uncertain_rate=round(uncertain / den, 4) if assessed_students > 0 else 0.0,
        )
        status_distributions.append(dist)

        # Average estimates
        if c_snaps:
            avg_mastery = sum(s.mastery_estimate for s in c_snaps) / len(c_snaps)
            avg_direct = sum(s.direct_estimate for s in c_snaps) / len(c_snaps)
            assessed_cnt = len(c_snaps)
        else:
            avg_mastery = 0.5
            avg_direct = 0.5
            assessed_cnt = 0

        average_mastery_list.append(
            AverageMasteryEstimate(
                concept_id=cid,
                concept_name=c_name,
                average_mastery_estimate=round(avg_mastery, 4),
                average_direct_estimate=round(avg_direct, 4),
                assessed_count=assessed_cnt,
            )
        )

    # 8. Common root gaps across assessed cohort
    diag_service = DiagnosisService(db)
    root_gap_counts = Counter()
    for stu_id, sess_id in latest_session_ids_by_student.items():
        diag_res = diag_service.compute_student_diagnosis(student_id=stu_id, session_id=sess_id)
        for rg in diag_res.root_gaps:
            root_gap_counts[rg.concept_id] += 1

    common_root_gaps: List[RootGapFrequencyItem] = []
    for cid, cnt in root_gap_counts.most_common():
        pct = round((cnt / assessed_students) * 100, 1) if assessed_students > 0 else 0.0
        common_root_gaps.append(
            RootGapFrequencyItem(
                concept_id=cid,
                concept_name=concepts_by_id.get(cid, cid),
                count=cnt,
                percentage_of_assessed=pct,
            )
        )

    # 9. Retest outcomes aggregate across authorized students
    retest_counter = Counter()
    total_retests = 0
    for s_id in student_ids:
        replay = replay_student_mastery_from_db(db, s_id)
        for cid, (outcome, _) in replay.retest_outcomes.items():
            if outcome != "not_verified":
                retest_counter[outcome] += 1
                total_retests += 1

    retest_summary = RetestOutcomesAggregate(
        recovered=retest_counter.get("recovered", 0),
        improving=retest_counter.get("improving", 0),
        no_change=retest_counter.get("no_change", 0),
        declined=retest_counter.get("declined", 0),
        not_verified=retest_counter.get("not_verified", 0),
        total_retests=total_retests,
    )

    return ClassAnalyticsResponse(
        class_id=target_class.id,
        class_name=target_class.name,
        class_code=target_class.code,
        section_id=target_section.id if target_section else None,
        section_name=target_section.name if target_section else None,
        section_code=target_section.code if target_section else None,
        total_students=total_students,
        assessed_students=assessed_students,
        diagnostic_completion_rate=completion_rate,
        denominator_description=(
            f"Percentages are calculated using assessed students (n={assessed_students}) as the denominator. "
            f"Students with no completed diagnostic assessment (n={total_students - assessed_students}) are excluded from rates."
        ),
        concepts_status_distribution=status_distributions,
        average_mastery_estimates=average_mastery_list,
        common_root_gaps=common_root_gaps,
        retest_outcomes=retest_summary,
    )


def _empty_analytics_response(
    target_class: Class,
    target_section: Optional[Section],
    topological_order: List[str],
    concepts_by_id: Dict[str, str],
) -> ClassAnalyticsResponse:
    """Return an honest empty analytics response when no students exist in scope."""
    status_distributions = [
        ConceptStatusDistribution(
            concept_id=cid,
            concept_name=concepts_by_id.get(cid, cid),
            mastered=0,
            confirmed_gap=0,
            suspected_gap=0,
            uncertain=0,
            unassessed=0,
            mastered_rate=0.0,
            confirmed_gap_rate=0.0,
            suspected_gap_rate=0.0,
            uncertain_rate=0.0,
        )
        for cid in topological_order
    ]
    avg_estimates = [
        AverageMasteryEstimate(
            concept_id=cid,
            concept_name=concepts_by_id.get(cid, cid),
            average_mastery_estimate=0.5,
            average_direct_estimate=0.5,
            assessed_count=0,
        )
        for cid in topological_order
    ]
    return ClassAnalyticsResponse(
        class_id=target_class.id,
        class_name=target_class.name,
        class_code=target_class.code,
        section_id=target_section.id if target_section else None,
        section_name=target_section.name if target_section else None,
        section_code=target_section.code if target_section else None,
        total_students=0,
        assessed_students=0,
        diagnostic_completion_rate=0.0,
        denominator_description="No students enrolled in the authorized scope.",
        concepts_status_distribution=status_distributions,
        average_mastery_estimates=avg_estimates,
        common_root_gaps=[],
        retest_outcomes=RetestOutcomesAggregate(),
    )
