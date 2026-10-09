"""Acceptance tests for curriculum data and content validation."""

import copy
import os
import pytest
from app.db.seed import (
    SeedValidationError,
    load_json_file,
    validate_curriculum_data,
)


@pytest.fixture
def data_paths():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "app", "data"))
    return {
        "concepts": os.path.join(data_dir, "concepts.json"),
        "questions": os.path.join(data_dir, "questions.json"),
        "resources": os.path.join(data_dir, "resources.json"),
    }


def test_production_seed_data_passes_strict_validation(data_paths):
    concepts_raw = load_json_file(data_paths["concepts"])
    questions_raw = load_json_file(data_paths["questions"])
    resources_raw = load_json_file(data_paths["resources"])

    graph_service, summary = validate_curriculum_data(concepts_raw, questions_raw, resources_raw)

    assert summary["concepts_count"] == 8
    assert summary["questions_count"] == 40
    assert summary["resources_count"] == 24

    for cid, counts in summary["per_concept_breakdown"].items():
        assert counts["total"] == 5, f"Concept {cid} should have 5 questions"
        assert counts["diagnostic"] == 3, f"Concept {cid} should have 3 diagnostic questions"
        assert counts["retest"] == 2, f"Concept {cid} should have 2 retest questions"
        assert counts["reviewed"] == 5, f"Concept {cid} questions should be reviewed"


def test_question_with_invalid_concept_rejected(data_paths):
    concepts_raw = load_json_file(data_paths["concepts"])
    questions_raw = copy.deepcopy(load_json_file(data_paths["questions"]))
    resources_raw = load_json_file(data_paths["resources"])

    questions_raw[0]["primary_concept_id"] = "INVALID_CID"

    with pytest.raises(SeedValidationError) as exc:
        validate_curriculum_data(concepts_raw, questions_raw, resources_raw)
    assert "references non-existent primary_concept_id" in str(exc.value.message)


def test_question_with_zero_or_multiple_correct_options_rejected(data_paths):
    concepts_raw = load_json_file(data_paths["concepts"])
    questions_raw = copy.deepcopy(load_json_file(data_paths["questions"]))
    resources_raw = load_json_file(data_paths["resources"])

    # Make all options false
    for opt in questions_raw[0]["options"]:
        opt["is_correct"] = False

    with pytest.raises(SeedValidationError) as exc:
        validate_curriculum_data(concepts_raw, questions_raw, resources_raw)
    assert "must have exactly 1 correct option; found 0" in str(exc.value.message)

    # Make two options true
    questions_raw[0]["options"][0]["is_correct"] = True
    questions_raw[0]["options"][1]["is_correct"] = True

    with pytest.raises(SeedValidationError) as exc:
        validate_curriculum_data(concepts_raw, questions_raw, resources_raw)
    assert "must have exactly 1 correct option; found 2" in str(exc.value.message)


def test_question_with_invalid_distractor_mapping_rejected(data_paths):
    concepts_raw = load_json_file(data_paths["concepts"])
    questions_raw = copy.deepcopy(load_json_file(data_paths["questions"]))
    resources_raw = load_json_file(data_paths["resources"])

    questions_raw[0]["options"][1]["maps_to_concept_id"] = "NON_EXISTENT_CID"

    with pytest.raises(SeedValidationError) as exc:
        validate_curriculum_data(concepts_raw, questions_raw, resources_raw)
    assert "maps to non-existent concept" in str(exc.value.message)


def test_question_with_invalid_difficulty_or_time_rejected(data_paths):
    concepts_raw = load_json_file(data_paths["concepts"])
    questions_raw = copy.deepcopy(load_json_file(data_paths["questions"]))
    resources_raw = load_json_file(data_paths["resources"])

    questions_raw[0]["difficulty"] = 10  # Out of range 1-5
    questions_raw[1]["expected_time_s"] = -5  # Non-positive

    with pytest.raises(SeedValidationError) as exc:
        validate_curriculum_data(concepts_raw, questions_raw, resources_raw)
    assert "difficulty '10' must be an integer between 1 and 5" in str(exc.value.message)
    assert "expected_time_s must be a positive number" in str(exc.value.message)


def test_retest_and_diagnostic_variant_group_overlap_rejected(data_paths):
    concepts_raw = load_json_file(data_paths["concepts"])
    questions_raw = copy.deepcopy(load_json_file(data_paths["questions"]))
    resources_raw = load_json_file(data_paths["resources"])

    # Give a retest item the exact same variant_group as a diagnostic item
    d_q = next(q for q in questions_raw if q["primary_concept_id"] == "D01" and q["use_for_diagnosis"])
    r_q = next(q for q in questions_raw if q["primary_concept_id"] == "D01" and q["use_for_retest"])
    r_q["variant_group"] = d_q["variant_group"]

    with pytest.raises(SeedValidationError) as exc:
        validate_curriculum_data(concepts_raw, questions_raw, resources_raw)
    assert "retest items share variant_group with diagnostic items" in str(exc.value.message)


def test_missing_resource_depths_rejected(data_paths):
    concepts_raw = load_json_file(data_paths["concepts"])
    questions_raw = load_json_file(data_paths["questions"])
    resources_raw = copy.deepcopy(load_json_file(data_paths["resources"]))

    # Remove deep_learning for D01
    resources_raw = [r for r in resources_raw if not (r["concept_id"] == "D01" and r["depth"] == "deep_learning")]

    with pytest.raises(SeedValidationError) as exc:
        validate_curriculum_data(concepts_raw, questions_raw, resources_raw)
    assert "Concept 'D01' is missing resources" in str(exc.value.message)
