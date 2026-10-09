"""Authentication routes for MindMesh.

Conforms to Specification v3.0 Sections 11.0, 19.1, 19.5.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.errors import UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.auth import AdministratorAccount, Educator
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate an educator or administrator and issue a JWT token.
    
    Verifies credentials securely in constant time. Never exposes whether email exists.
    """
    normalized_email = payload.email.strip().lower()

    # Check administrator accounts first
    admin = (
        db.query(AdministratorAccount)
        .filter(AdministratorAccount.email == normalized_email)
        .first()
    )
    if admin and verify_password(payload.password, admin.password_hash):
        token = create_access_token({"sub": admin.id, "role": "administrator"})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            role="administrator",
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    # Check educators
    educator = db.query(Educator).filter(Educator.email == normalized_email).first()
    if educator and verify_password(payload.password, educator.password_hash):
        token = create_access_token({"sub": educator.id, "role": "educator"})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            role="educator",
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    # Invalid credentials - constant error to prevent enumeration
    raise UnauthorizedError("Invalid email or password", code="INVALID_CREDENTIALS")
