"""One-time Administrator CLI Bootstrap for MindMesh.

Specification v3.0 Sections 19.2, 21:
- Creates the first administrator using credentials supplied through environment
  variables (ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NAME) or securely prompted input.
- Refuses to create a second initial administrator if one already exists.
- Never prints passwords, secrets, or exposes an admin-creation HTTP endpoint.
"""

import getpass
import os
import sys
from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.auth import AdministratorAccount


class BootstrapError(Exception):
    """Raised when bootstrap prerequisites are not met."""
    pass


def bootstrap_initial_admin(
    email: Optional[str] = None,
    password: Optional[str] = None,
    display_name: Optional[str] = None,
    db: Optional[Session] = None,
) -> AdministratorAccount:
    """Bootstrap the initial administrator account.
    
    Ensures exactly one-time execution. Raises BootstrapError if an administrator
    already exists or if valid credentials are not provided.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # Atomic check: refuse if any administrator already exists
        existing_admin = db.query(AdministratorAccount).first()
        if existing_admin:
            raise BootstrapError(
                "Bootstrap refused: an administrator account already exists. "
                "Initial administrator creation is strictly a one-time operation."
            )

        # Resolve credentials from arguments, environment, or secure prompt
        admin_email = email or os.getenv("ADMIN_EMAIL")
        admin_password = password or os.getenv("ADMIN_PASSWORD")
        admin_name = display_name or os.getenv("ADMIN_NAME") or "System Administrator"

        if not admin_email and sys.stdin.isatty():
            admin_email = input("Enter administrator email: ").strip()

        if not admin_password and sys.stdin.isatty():
            admin_password = getpass.getpass("Enter administrator password: ")

        if not admin_email or not admin_email.strip():
            raise BootstrapError("Administrator email is required.")

        if not admin_password or len(admin_password) < 8:
            raise BootstrapError("Administrator password must be at least 8 characters.")

        normalized_email = admin_email.strip().lower()

        hashed_pw = hash_password(admin_password)
        admin = AdministratorAccount(
            email=normalized_email,
            password_hash=hashed_pw,
            display_name=admin_name.strip(),
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    finally:
        if close_db:
            db.close()


def main() -> None:
    """CLI entrypoint for administrator bootstrap."""
    try:
        admin = bootstrap_initial_admin()
        print(f"Successfully bootstrapped initial administrator: {admin.email} ({admin.id})")
        sys.exit(0)
    except BootstrapError as exc:
        print(f"Bootstrap failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error during administrator bootstrap: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
