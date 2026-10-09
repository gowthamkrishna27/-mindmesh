"""Test Alembic migrations environment and clean database upgrade.

Conforms to Specification v3.0 Sections 12, 13.
"""

import os
import sqlite3
import tempfile
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_script_directory_and_revisions():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    alembic_ini_path = os.path.join(backend_dir, "alembic.ini")
    assert os.path.exists(alembic_ini_path)

    alembic_cfg = Config(alembic_ini_path)
    script = ScriptDirectory.from_config(alembic_cfg)
    heads = script.get_heads()
    assert len(heads) == 1
    assert heads[0] is not None


def test_clean_database_migration_upgrade():
    """Verify all migrations apply cleanly in order from scratch to a fresh database."""
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    alembic_ini_path = os.path.join(backend_dir, "alembic.ini")

    # Use a temporary file for clean sqlite database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name

    try:
        alembic_cfg = Config(alembic_ini_path)
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{tmp_db_path}")

        # Upgrade from 0 to head
        command.upgrade(alembic_cfg, "head")

        # Verify tables created
        con = sqlite3.connect(tmp_db_path)
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        con.close()

        expected_tables = {
            "concepts",
            "prerequisite_edges",
            "questions",
            "question_options",
            "question_hints",
            "resources",
            "students",
            "sessions",
            "session_question_issues",
            "interaction_events",
            "responses",
            "response_evidence",
            "concept_epochs",
            "student_concept_mastery",
            "diagnosis_snapshots",
            "learning_completions",
            "administrator_accounts",
            "educators",
            "classes",
            "sections",
            "educator_class_assignments",
            "admin_audit_events",
        }
        for expected in expected_tables:
            assert expected in tables, f"Expected table '{expected}' not found after upgrade."

    finally:
        if os.path.exists(tmp_db_path):
            os.remove(tmp_db_path)
