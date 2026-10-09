"""Unit tests for database session and engine."""

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine, get_db


def test_base_metadata():
    assert Base.metadata is not None


def test_database_connectivity(db_session: Session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_get_db_generator():
    db_gen = get_db()
    db = next(db_gen)
    assert isinstance(db, Session)
    try:
        res = db.execute(text("SELECT 1")).scalar()
        assert res == 1
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass
