"""Administrator routes for educator approvals, suspensions, and assignments.

Conforms to Specification v3.0 Sections 11.0, 19.2, 19.3, 19.5.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.auth import require_admin
from app.db.session import get_db
from app.models.auth import AdministratorAccount
from app.schemas.auth import (
    AdminEducatorItem,
    AssignmentCreateRequest,
    AssignmentResponse,
    EducatorApprovalResponse,
    EducatorSuspensionResponse,
)
from app.services.admin_service import (
    approve_educator,
    create_assignment,
    get_educator_assignments,
    list_educators,
    reject_educator,
    revoke_assignment,
    suspend_educator,
)

router = APIRouter(prefix="/admin", tags=["Administrator"])


@router.get("/educators", response_model=List[AdminEducatorItem])
def get_educators(
    status: Optional[str] = Query(None, description="Filter by status (e.g. pending, approved, suspended)"),
    admin: AdministratorAccount = Depends(require_admin),
    db: Session = Depends(get_db),
) -> List[AdminEducatorItem]:
    """List educator accounts for administrative review."""
    return list_educators(status_filter=status, db=db)


@router.post("/educators/{educator_id}/approve", response_model=EducatorApprovalResponse)
def approve_educator_route(
    educator_id: str,
    admin: AdministratorAccount = Depends(require_admin),
    db: Session = Depends(get_db),
) -> EducatorApprovalResponse:
    """Approve a pending educator application."""
    educator = approve_educator(admin_id=admin.id, educator_id=educator_id, db=db)
    return EducatorApprovalResponse(
        id=educator.id,
        email=educator.email,
        status=educator.status,
        approved_at=educator.approved_at,
        approved_by_admin_id=educator.approved_by_admin_id,
    )


@router.post("/educators/{educator_id}/reject", response_model=EducatorSuspensionResponse)
def reject_educator_route(
    educator_id: str,
    admin: AdministratorAccount = Depends(require_admin),
    db: Session = Depends(get_db),
) -> EducatorSuspensionResponse:
    """Reject a pending educator application."""
    educator = reject_educator(admin_id=admin.id, educator_id=educator_id, db=db)
    return EducatorSuspensionResponse(
        id=educator.id,
        email=educator.email,
        status=educator.status,
    )


@router.post("/educators/{educator_id}/suspend", response_model=EducatorSuspensionResponse)
def suspend_educator_route(
    educator_id: str,
    admin: AdministratorAccount = Depends(require_admin),
    db: Session = Depends(get_db),
) -> EducatorSuspensionResponse:
    """Suspend/revoke educator access. Takes effect immediately on the next request."""
    educator = suspend_educator(admin_id=admin.id, educator_id=educator_id, db=db)
    return EducatorSuspensionResponse(
        id=educator.id,
        email=educator.email,
        status=educator.status,
    )


@router.post(
    "/educators/{educator_id}/assignments",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assignment_route(
    educator_id: str,
    payload: AssignmentCreateRequest,
    admin: AdministratorAccount = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AssignmentResponse:
    """Assign an approved educator to a class and optional section."""
    assignment = create_assignment(
        admin_id=admin.id,
        educator_id=educator_id,
        class_id=payload.class_id,
        section_id=payload.section_id,
        db=db,
    )
    return assignment


@router.delete(
    "/educators/{educator_id}/assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def revoke_assignment_route(
    educator_id: str,
    assignment_id: str,
    admin: AdministratorAccount = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    """Revoke an educator's assignment. Takes effect immediately on the next request."""
    revoke_assignment(
        admin_id=admin.id,
        educator_id=educator_id,
        assignment_id=assignment_id,
        db=db,
    )


@router.get("/educators/{educator_id}/assignments", response_model=List[AssignmentResponse])
def get_assignments_route(
    educator_id: str,
    admin: AdministratorAccount = Depends(require_admin),
    db: Session = Depends(get_db),
) -> List[AssignmentResponse]:
    """Inspect all assignments (active and revoked) for an educator."""
    return get_educator_assignments(educator_id=educator_id, db=db)
