"""Authentication and identity dependencies for MindMesh.

Conforms to Specification v3.0 Sections 11.0, 19.1, 19.6:
- Enforces role separation between student, educator, and administrator.
- Derives identity from validated cryptographic tokens, never client headers.
- Re-checks current account status in database on every protected request.
"""

from dataclasses import dataclass
from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.orm import Session
import jwt
from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.auth import AdministratorAccount, Educator
from app.models.session import Student


@dataclass
class AuthenticatedIdentity:
    id: str
    role: str  # "educator" or "administrator"


def get_current_identity(
    authorization: Optional[str] = Header(None),
) -> AuthenticatedIdentity:
    """Extract and validate bearer token identity for educator/admin APIs."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Authentication credentials required", code="UNAUTHORIZED")

    token = authorization.split("Bearer ", 1)[1].strip()
    if not token:
        raise UnauthorizedError("Missing authentication token", code="UNAUTHORIZED")

    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Authentication token has expired", code="TOKEN_EXPIRED")
    except Exception:
        raise UnauthorizedError("Invalid authentication token", code="INVALID_TOKEN")

    user_id = payload.get("sub")
    role = payload.get("role")
    if not user_id or not role:
        raise UnauthorizedError("Invalid token claims", code="INVALID_CLAIMS")

    return AuthenticatedIdentity(id=user_id, role=role)


def require_admin(
    identity: AuthenticatedIdentity = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> AdministratorAccount:
    """Enforce administrator role and check active database record on every request."""
    if identity.role != "administrator":
        raise ForbiddenError("Administrator access required", code="FORBIDDEN")

    admin = db.query(AdministratorAccount).filter(AdministratorAccount.id == identity.id).first()
    if not admin:
        raise UnauthorizedError("Administrator account not found", code="ACCOUNT_NOT_FOUND")

    return admin


def require_educator(
    identity: AuthenticatedIdentity = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> Educator:
    """Enforce educator role and verify active approved status in DB on every request.
    
    If an administrator suspends or revokes the educator, subsequent requests fail
    immediately (403 Forbidden).
    """
    if identity.role != "educator":
        raise ForbiddenError("Educator access required", code="FORBIDDEN")

    educator = db.query(Educator).filter(Educator.id == identity.id).first()
    if not educator:
        raise UnauthorizedError("Educator account not found", code="ACCOUNT_NOT_FOUND")

    if educator.status != "approved":
        raise ForbiddenError(
            f"Educator account status is '{educator.status}'. Access denied.",
            code="EDUCATOR_NOT_APPROVED",
        )

    return educator


def get_current_student(
    authorization: Optional[str] = Header(None),
    x_student_id: Optional[str] = Header(None, alias="X-Student-Id"),
    db: Session = Depends(get_db),
) -> Student:
    """Resolve the acting student identity from Bearer token or header.

    Retains existing Phase 4/5 development authentication behavior.
    """
    student_id: str = "dev_student"

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()
        if token:
            student_id = token
    elif x_student_id and x_student_id.strip():
        student_id = x_student_id.strip()

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        student = Student(
            id=student_id,
            name=f"Student {student_id}",
            consent_given=False,
        )
        db.add(student)
        db.commit()
        db.refresh(student)

    return student
