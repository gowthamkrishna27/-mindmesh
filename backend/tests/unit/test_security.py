"""Unit tests for security, cryptography, and administrator bootstrap.

Conforms to Specification v3.0 Sections 11.0, 19.1, 19.2, 19.6.
"""

from datetime import timedelta
import pytest
from sqlalchemy.orm import Session
from app.core.bootstrap_admin import BootstrapError, bootstrap_initial_admin
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.auth import AdministratorAccount


def test_password_hashing_and_verification():
    """Verify bcrypt password hashing, unique salts, and constant-time verification."""
    password = "SuperSecretPassword123!"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Different salts produce different hashes
    assert hash1 != hash2
    assert hash1.startswith("$2b$")

    # Verification
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True
    assert verify_password("WrongPassword123!", hash1) is False
    assert verify_password("", hash1) is False
    assert verify_password(password, "invalid_hash_string") is False


def test_access_token_creation_and_expiration():
    """Verify JWT access token creation, claims, and expiration."""
    data = {"sub": "user_123", "role": "educator"}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload["sub"] == "user_123"
    assert payload["role"] == "educator"
    assert "exp" in payload
    assert "iat" in payload

    # Expired token
    expired_token = create_access_token(data, expires_delta=timedelta(seconds=-10))
    with pytest.raises(Exception):
        decode_access_token(expired_token)


def test_administrator_bootstrap_one_time_enforcement(db_session: Session):
    """Verify that administrator bootstrap works once and strictly refuses a second creation."""
    # First bootstrap
    admin = bootstrap_initial_admin(
        email="admin@mindmesh.org",
        password="AdminSecurePassword123!",
        display_name="Lead Admin",
        db=db_session,
    )
    assert admin.id is not None
    assert admin.email == "admin@mindmesh.org"
    assert admin.display_name == "Lead Admin"
    assert admin.password_hash != "AdminSecurePassword123!"
    assert verify_password("AdminSecurePassword123!", admin.password_hash) is True

    # Second bootstrap attempt must fail
    with pytest.raises(BootstrapError) as exc_info:
        bootstrap_initial_admin(
            email="another_admin@mindmesh.org",
            password="AnotherPassword123!",
            display_name="Second Admin",
            db=db_session,
        )
    assert "strictly a one-time operation" in str(exc_info.value)

    # Ensure only 1 admin exists in the database
    count = db_session.query(AdministratorAccount).count()
    assert count == 1


def test_administrator_bootstrap_validation(db_session: Session):
    """Verify that bootstrap rejects missing or too-short passwords."""
    with pytest.raises(BootstrapError) as exc:
        bootstrap_initial_admin(email="", password="ValidPassword123!", db=db_session)
    assert "email is required" in str(exc.value)

    with pytest.raises(BootstrapError) as exc:
        bootstrap_initial_admin(email="test@mindmesh.org", password="short", db=db_session)
    assert "at least 8 characters" in str(exc.value)
