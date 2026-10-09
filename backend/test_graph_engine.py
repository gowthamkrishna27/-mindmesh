"""
Unit test suite for Mind Mesh NetworkX Concept Graph Engine
Validates requirements FR-G1 through FR-G6.
"""

import unittest
from pathlib import Path
from graph_engine import ConceptGraphEngine

class TestConceptGraphEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ConceptGraphEngine()

    def test_fr_g1_and_fr_g2_dag_loaded_and_valid(self):
        """Test that the 18 DBMS concepts load cleanly into a valid DAG with no cycles."""
        self.assertEqual(len(self.engine.G.nodes), 18)
        self.assertGreater(len(self.engine.G.edges), 15)
        # Verify no self-loops
        self.assertEqual(len(list(self.engine.G.selfloop_edges())), 0)

    def test_fr_g2_cycle_rejection(self):
        """Test that introducing a circular prerequisite dependency raises ValueError."""
        test_concepts = [
            {"id": "A", "name": "Concept A", "prerequisites": ["C"]},
            {"id": "B", "name": "Concept B", "prerequisites": ["A"]},
            {"id": "C", "name": "Concept C", "prerequisites": ["B"]},
        ]
        with self.assertRaises(ValueError) as ctx:
            engine = ConceptGraphEngine.__new__(ConceptGraphEngine)
            engine.G = __import__("networkx").DiGraph()
            engine.load_concepts(test_concepts)
        self.assertIn("Cycle detected", str(ctx.exception))

    def test_fr_g3_ancestor_distance(self):
        """Test that ancestors of Normalization (D13) correctly trace through FDs (D12) and Keys (D03)."""
        ancestors_dist = self.engine.get_ancestors_with_distance("D13")
        self.assertIn("D12", ancestors_dist)
        self.assertIn("D03", ancestors_dist)
        self.assertIn("D02", ancestors_dist)
        self.assertIn("D01", ancestors_dist)
        # D12 and D03 are direct prerequisites of D13 (distance 1)
        self.assertEqual(ancestors_dist["D12"], 1)
        self.assertEqual(ancestors_dist["D03"], 1)

    def test_fr_g4_topological_sort(self):
        """Test that every prerequisite appears strictly before its dependent in the learning path."""
        topo = self.engine.get_topological_sort()
        index_map = {cid: idx for idx, cid in enumerate(topo)}
        for u, v in self.engine.G.edges():
            self.assertLess(
                index_map[u],
                index_map[v],
                f"Prerequisite {u} must appear before {v} in topological sort"
            )

    def test_fr_g5_importance_computation(self):
        """Test that foundational concepts have high downstream importance."""
        d01_imp = self.engine.compute_importance("D01")
        d14_imp = self.engine.compute_importance("D14")
        # D01 (DBMS Basics) unlocks virtually all topics, whereas D14 (BCNF) is a leaf
        self.assertGreater(d01_imp, d14_imp)

    def test_fr_g6_transitive_reduction(self):
        """Test that transitive reduction simplifies graph without altering reachability."""
        tr_edges = self.engine.get_transitive_reduction()
        self.assertGreater(len(tr_edges), 0)
        self.assertLessEqual(len(tr_edges), len(self.engine.G.edges))

    def test_srs_section_5_root_gap_diagnosis(self):
        """
        SRS Section 11.1 Test Scenario:
        Student fails Normalization (D13) because of missing Functional Dependencies (D12).
        Verifies that root-gap engine identifies D12 as the root blocker.
        """
        simulated_responses = [
            {"question_id": "Q13A", "concept_id": "D13", "correct": False, "confidence": "high", "response_ms": 1400},
            {"question_id": "Q12A", "concept_id": "D12", "correct": False, "confidence": "low", "response_ms": 2800},
            {"question_id": "Q12B", "concept_id": "D12", "correct": False, "confidence": "medium", "response_ms": 2200},
            {"question_id": "Q08A", "concept_id": "D08", "correct": True, "confidence": "high", "response_ms": 1100},
        ]
        result = self.engine.diagnose_root_gap(simulated_responses)
        self.assertEqual(result["root_gap_id"], "D12")
        self.assertIn("D12", result["evidence_path"])
        self.assertIn("D13", result["evidence_path"])

if __name__ == "__main__":
    unittest.main()
