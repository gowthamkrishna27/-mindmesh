"""Acceptance tests for GraphService and NetworkX dependency graph validation."""

import pytest
from app.services.graph import (
    GraphService,
    GraphValidationError,
    load_graph_from_data,
)


@pytest.fixture
def sample_concepts_data():
    return [
        {"id": "D01", "name": "DBMS Basics", "prerequisites": []},
        {"id": "D02", "name": "Relational Model", "prerequisites": ["D01"]},
        {"id": "D03", "name": "Keys", "prerequisites": ["D02"]},
        {"id": "D04", "name": "Integrity Constraints", "prerequisites": ["D02", "D03"]},
        {"id": "D08", "name": "SQL Basics", "prerequisites": ["D02"]},
        {"id": "D09", "name": "SQL Joins", "prerequisites": ["D08"]},
        {"id": "D12", "name": "Functional Dependencies", "prerequisites": ["D03"]},
        {"id": "D13", "name": "Normalization (1NF-3NF)", "prerequisites": ["D03", "D12"]},
    ]


def test_valid_graph_construction(sample_concepts_data):
    graph = load_graph_from_data(sample_concepts_data, validate_expected=True)
    assert graph.graph.number_of_nodes() == 8
    assert graph.graph.number_of_edges() == 9


def test_missing_expected_concept_fails():
    incomplete = [
        {"id": "D01", "prerequisites": []},
        {"id": "D02", "prerequisites": ["D01"]},
    ]
    with pytest.raises(GraphValidationError) as exc:
        load_graph_from_data(incomplete, validate_expected=True)
    assert "missing required curriculum concepts" in str(exc.value.message)


def test_self_edge_rejected():
    with pytest.raises(GraphValidationError) as exc:
        GraphService(concept_ids=["D01"], edges=[("D01", "D01")])
    assert "Self-edge detected" in str(exc.value.message)


def test_duplicate_edge_rejected():
    with pytest.raises(GraphValidationError) as exc:
        GraphService(concept_ids=["D01", "D02"], edges=[("D01", "D02"), ("D01", "D02")])
    assert "Duplicate prerequisite edge detected" in str(exc.value.message)


def test_missing_endpoint_rejected():
    with pytest.raises(GraphValidationError) as exc:
        GraphService(concept_ids=["D01"], edges=[("D01", "NON_EXISTENT")])
    assert "non-existent dependent concept" in str(exc.value.message)

    with pytest.raises(GraphValidationError) as exc:
        GraphService(concept_ids=["D02"], edges=[("NON_EXISTENT", "D02")])
    assert "non-existent prerequisite concept" in str(exc.value.message)


def test_cycle_detection():
    # D01 -> D02 -> D03 -> D01
    cycle_edges = [("D01", "D02"), ("D02", "D03"), ("D03", "D01")]
    with pytest.raises(GraphValidationError) as exc:
        GraphService(concept_ids=["D01", "D02", "D03"], edges=cycle_edges)
    assert "Cycle detected" in str(exc.value.message)


def test_correct_prerequisite_direction_and_traversal(sample_concepts_data):
    graph = load_graph_from_data(sample_concepts_data)

    # D02 direct prereq is D01, direct dependents are D03, D04, D08
    assert graph.get_direct_prerequisites("D02") == {"D01"}
    assert graph.get_direct_dependents("D02") == {"D03", "D04", "D08"}

    # D13 direct prerequisites are D03 and D12
    assert graph.get_direct_prerequisites("D13") == {"D03", "D12"}


def test_ancestors_and_descendants(sample_concepts_data):
    graph = load_graph_from_data(sample_concepts_data)

    # Transitive ancestors of D09: D08, D02, D01
    assert graph.get_ancestors("D09") == {"D08", "D02", "D01"}

    # Transitive ancestors of D13: D01, D02, D03, D12
    assert graph.get_ancestors("D13") == {"D01", "D02", "D03", "D12"}

    # Transitive descendants of D01 (all 7 other concepts)
    assert graph.get_descendants("D01") == {"D02", "D03", "D04", "D08", "D09", "D12", "D13"}

    # Leaf nodes have 0 descendants
    assert graph.get_descendants("D04") == set()
    assert graph.get_descendants("D09") == set()
    assert graph.get_descendants("D13") == set()


def test_importance_calculation_matches_spec_v3(sample_concepts_data):
    graph = load_graph_from_data(sample_concepts_data)

    # Section 4 exact importance fractions:
    # D01 7/7 (1.0), D02 6/7 (0.8571), D03 3/7 (0.4286), D08 1/7 (0.1429), D12 1/7 (0.1429), others 0
    assert graph.get_descendant_count("D01") == 7
    assert pytest.approx(graph.get_importance("D01"), 0.001) == 1.0

    assert graph.get_descendant_count("D02") == 6
    assert pytest.approx(graph.get_importance("D02"), 0.001) == 6.0 / 7.0

    assert graph.get_descendant_count("D03") == 3
    assert pytest.approx(graph.get_importance("D03"), 0.001) == 3.0 / 7.0

    assert graph.get_descendant_count("D08") == 1
    assert pytest.approx(graph.get_importance("D08"), 0.001) == 1.0 / 7.0

    assert graph.get_descendant_count("D12") == 1
    assert pytest.approx(graph.get_importance("D12"), 0.001) == 1.0 / 7.0

    assert graph.get_descendant_count("D04") == 0
    assert graph.get_importance("D04") == 0.0

    assert graph.get_descendant_count("D09") == 0
    assert graph.get_importance("D09") == 0.0

    assert graph.get_descendant_count("D13") == 0
    assert graph.get_importance("D13") == 0.0


def test_root_detection(sample_concepts_data):
    graph = load_graph_from_data(sample_concepts_data)
    assert graph.is_root("D01") is True
    assert graph.is_root("D02") is False
    assert graph.is_root("D03") is False


def test_topological_sort_is_deterministic(sample_concepts_data):
    graph = load_graph_from_data(sample_concepts_data)
    order_1 = graph.get_topological_order()
    order_2 = graph.get_topological_order()
    assert order_1 == order_2

    # Prerequisite must always precede dependent
    for prereq, dependent in graph.raw_edges:
        assert order_1.index(prereq) < order_1.index(dependent)


def test_unlocked_calculation(sample_concepts_data):
    graph = load_graph_from_data(sample_concepts_data)

    # When no concepts are ready:
    # D01 has no prerequisites, so it is unlocked
    assert graph.is_unlocked("D01", ready_concept_ids=set()) is True
    # D02 requires D01, so not unlocked
    assert graph.is_unlocked("D02", ready_concept_ids=set()) is False

    # Once D01 is ready:
    ready = {"D01"}
    # D01 is ready so it is no longer an active unlocked target
    assert graph.is_unlocked("D01", ready_concept_ids=ready) is False
    # D02 prerequisite (D01) is satisfied, so D02 is unlocked
    assert graph.is_unlocked("D02", ready_concept_ids=ready) is True
    # D03 still requires D02, so not unlocked
    assert graph.is_unlocked("D03", ready_concept_ids=ready) is False

    # Multi-prerequisite node: D13 requires both D03 and D12
    assert graph.is_unlocked("D13", ready_concept_ids={"D01", "D02", "D03"}) is False
    assert graph.is_unlocked("D13", ready_concept_ids={"D01", "D02", "D03", "D12"}) is True
