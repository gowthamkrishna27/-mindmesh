"""NetworkX-based concept dependency graph service.

Edge direction: prerequisite -> dependent.
Conforms to Specification v3.0 Sections 4, 8, 9, 14.
"""

from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
import networkx as nx
from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.models.curriculum import Concept, PrerequisiteEdge


class GraphValidationError(AppError):
    """Raised when the curriculum concept graph violates DAG or structural constraints."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message=message, code="GRAPH_VALIDATION_ERROR", status_code=500, details=details)


EXPECTED_DBMS_CONCEPTS: List[str] = ["D01", "D02", "D03", "D04", "D08", "D09", "D12", "D13"]
IMPORTANCE_DENOMINATOR: int = 7


class GraphService:
    """Service for querying and validating the concept dependency graph."""

    def __init__(
        self,
        concept_ids: Iterable[str],
        edges: Iterable[Tuple[str, str]],
        validate_expected: bool = False,
    ) -> None:
        self.raw_concept_ids: List[str] = list(concept_ids)
        self.raw_edges: List[Tuple[str, str]] = list(edges)
        self.graph: nx.DiGraph = nx.DiGraph()
        self._build_and_validate(validate_expected=validate_expected)

    def _build_and_validate(self, validate_expected: bool = False) -> None:
        concept_set = set(self.raw_concept_ids)

        if validate_expected:
            missing_expected = set(EXPECTED_DBMS_CONCEPTS) - concept_set
            if missing_expected:
                raise GraphValidationError(
                    f"Graph is missing required curriculum concepts: {sorted(missing_expected)}",
                    details={"missing_concepts": sorted(missing_expected)},
                )

        # Add all concept nodes
        for cid in self.raw_concept_ids:
            self.graph.add_node(cid)

        # Track edges to detect duplicates
        seen_edges: Set[Tuple[str, str]] = set()

        for prereq, dependent in self.raw_edges:
            # 1. Reject self-edges
            if prereq == dependent:
                raise GraphValidationError(
                    f"Self-edge detected on concept '{prereq}'. A concept cannot be a prerequisite of itself.",
                    details={"concept_id": prereq},
                )

            # 2. Reject duplicate edges
            edge_tuple = (prereq, dependent)
            if edge_tuple in seen_edges:
                raise GraphValidationError(
                    f"Duplicate prerequisite edge detected: {prereq} -> {dependent}",
                    details={"prerequisite": prereq, "dependent": dependent},
                )
            seen_edges.add(edge_tuple)

            # 3. Reject missing endpoints
            if prereq not in concept_set:
                raise GraphValidationError(
                    f"Edge references non-existent prerequisite concept: '{prereq}' in edge {prereq} -> {dependent}",
                    details={"prerequisite": prereq, "dependent": dependent},
                )
            if dependent not in concept_set:
                raise GraphValidationError(
                    f"Edge references non-existent dependent concept: '{dependent}' in edge {prereq} -> {dependent}",
                    details={"prerequisite": prereq, "dependent": dependent},
                )

            self.graph.add_edge(prereq, dependent)

        # 4. Check for cycles
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            cycle_desc = " -> ".join(cycles[0]) + f" -> {cycles[0][0]}" if cycles else "cycle"
            raise GraphValidationError(
                f"Cycle detected in prerequisite graph: {cycle_desc}. Prerequisite graph must be a DAG.",
                details={"cycles": cycles},
            )

    def get_direct_prerequisites(self, concept_id: str) -> Set[str]:
        """Return direct prerequisite concept IDs (in-edges)."""
        self._ensure_concept_exists(concept_id)
        return set(self.graph.predecessors(concept_id))

    def get_direct_dependents(self, concept_id: str) -> Set[str]:
        """Return direct dependent concept IDs (out-edges)."""
        self._ensure_concept_exists(concept_id)
        return set(self.graph.successors(concept_id))

    def get_ancestors(self, concept_id: str) -> Set[str]:
        """Return all transitive prerequisites (ancestors in DAG)."""
        self._ensure_concept_exists(concept_id)
        return nx.ancestors(self.graph, concept_id)

    def get_descendants(self, concept_id: str) -> Set[str]:
        """Return all transitive dependents (descendants in DAG)."""
        self._ensure_concept_exists(concept_id)
        return nx.descendants(self.graph, concept_id)

    def get_descendant_count(self, concept_id: str) -> int:
        """Count of transitive descendants."""
        return len(self.get_descendants(concept_id))

    def get_importance(self, concept_id: str, denominator: int = IMPORTANCE_DENOMINATOR) -> float:
        """Calculate importance score: descendant_count / denominator (Section 4)."""
        if denominator <= 0:
            return 0.0
        return self.get_descendant_count(concept_id) / float(denominator)

    def is_root(self, concept_id: str) -> bool:
        """True if the concept has no prerequisites (in-degree 0)."""
        self._ensure_concept_exists(concept_id)
        return self.graph.in_degree(concept_id) == 0

    def get_topological_order(self) -> List[str]:
        """Return a deterministic topological sort order (prerequisites before dependents).

        Uses lexicographical topological sort keyed by concept ID for 100% reproducible tie-breaking.
        """
        return list(nx.lexicographical_topological_sort(self.graph, key=lambda node: str(node)))

    def is_unlocked(self, concept_id: str, ready_concept_ids: Set[str]) -> bool:
        """Determine if concept is unlocked: not yet ready/mastered and all direct prerequisites are ready (Section 9.4)."""
        self._ensure_concept_exists(concept_id)
        if concept_id in ready_concept_ids:
            return False
        direct_prereqs = self.get_direct_prerequisites(concept_id)
        return direct_prereqs.issubset(ready_concept_ids)

    def get_unlocked_concepts(self, ready_concept_ids: Set[str]) -> List[str]:
        """Return list of all currently unlocked concepts in topological order."""
        ordered = self.get_topological_order()
        return [cid for cid in ordered if self.is_unlocked(cid, ready_concept_ids)]

    def _ensure_concept_exists(self, concept_id: str) -> None:
        if concept_id not in self.graph:
            raise GraphValidationError(f"Concept '{concept_id}' does not exist in graph.")


def load_graph_from_data(concepts_data: List[Dict[str, Any]], validate_expected: bool = True) -> GraphService:
    """Build GraphService from raw JSON/dict concepts data."""
    concept_ids = [c["id"] for c in concepts_data]
    edges: List[Tuple[str, str]] = []
    for c in concepts_data:
        dependent_id = c["id"]
        for prereq_id in c.get("prerequisites", []):
            edges.append((prereq_id, dependent_id))
    return GraphService(concept_ids=concept_ids, edges=edges, validate_expected=validate_expected)


def load_graph_from_db(db: Session, validate_expected: bool = True) -> GraphService:
    """Build GraphService by reading concepts and prerequisite_edges from database."""
    concepts = db.query(Concept.id).all()
    concept_ids = [c[0] for c in concepts]

    edges_query = db.query(PrerequisiteEdge.prerequisite_id, PrerequisiteEdge.dependent_id).all()
    edges = [(e[0], e[1]) for e in edges_query]

    return GraphService(concept_ids=concept_ids, edges=edges, validate_expected=validate_expected)
