"""Acceptance tests for database seeding pipeline."""

import copy
import os
import pytest
from sqlalchemy.orm import Session
from app.db.seed import (
    SeedValidationError,
    load_json_file,
    seed_curriculum,
)
from app.models.curriculum import (
    Concept,
    PrerequisiteEdge,
    Question,
    QuestionOption,
    QuestionHint,
    Resource,
)


@pytest.fixture
def data_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "app", "data"))


def test_seed_into_empty_database(db_session: Session, data_dir: str):
    summary = seed_curriculum(db_session, data_dir=data_dir)

    assert summary["concepts_count"] == 8
    assert summary["edges_count"] == 9
    assert summary["questions_count"] == 40
    assert summary["resources_count"] == 24

    assert db_session.query(Concept).count() == 8
    assert db_session.query(PrerequisiteEdge).count() == 9
    assert db_session.query(Question).count() == 40
    assert db_session.query(QuestionOption).count() == 160  # 40 * 4
    assert db_session.query(QuestionHint).count() == 80    # 40 * 2
    assert db_session.query(Resource).count() == 24        # 8 * 3


def test_repeated_seed_is_idempotent(db_session: Session, data_dir: str):
    # First seed
    seed_curriculum(db_session, data_dir=data_dir)
    initial_concepts = db_session.query(Concept).count()
    initial_questions = db_session.query(Question).count()
    initial_options = db_session.query(QuestionOption).count()

    # Second seed
    seed_curriculum(db_session, data_dir=data_dir)
    assert db_session.query(Concept).count() == initial_concepts
    assert db_session.query(Question).count() == initial_questions
    assert db_session.query(QuestionOption).count() == initial_options


def test_failed_validation_rolls_back_cleanly(db_session: Session, tmp_path):
    # Create corrupted data in temp directory
    real_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "app", "data"))
    concepts_raw = load_json_file(os.path.join(real_data_dir, "concepts.json"))
    questions_raw = load_json_file(os.path.join(real_data_dir, "questions.json"))
    resources_raw = load_json_file(os.path.join(real_data_dir, "resources.json"))

    # Introduce a cycle in concepts: D01 -> D02 -> D01
    concepts_corrupt = copy.deepcopy(concepts_raw)
    concepts_corrupt[0]["prerequisites"] = ["D02"]

    import json
    with open(tmp_path / "concepts.json", "w") as f:
        json.dump(concepts_corrupt, f)
    with open(tmp_path / "questions.json", "w") as f:
        json.dump(questions_raw, f)
    with open(tmp_path / "resources.json", "w") as f:
        json.dump(resources_raw, f)

    initial_concept_count = db_session.query(Concept).count()

    with pytest.raises(SeedValidationError):
        seed_curriculum(db_session, data_dir=str(tmp_path))

    # Verify no partial inserts occurred
    assert db_session.query(Concept).count() == initial_concept_count
