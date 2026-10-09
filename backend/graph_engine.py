"""
Mind Mesh Concept Graph Engine powered by NetworkX
Implements SRS Section 3, Section 5, and Section 6.1 (FR-G1 to FR-G6).
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
import networkx as nx  # type: ignore

class ConceptGraphEngine:
    def __init__(self, concepts_path: Optional[Path] = None, questions_path: Optional[Path] = None):
        self.G = nx.DiGraph()
        self.concepts_data: Dict[str, Dict[str, Any]] = {}
        self.questions_data: Dict[str, Dict[str, Any]] = {}
        
        base_dir = Path(__file__).parent / "data"
        c_path = concepts_path or (base_dir / "concepts.json")
        q_path = questions_path or (base_dir / "questions.json")
        
        if c_path.exists():
            with open(c_path, "r", encoding="utf-8") as f:
                concepts_list = json.load(f)
                self.load_concepts(concepts_list)
                
        if q_path.exists():
            with open(q_path, "r", encoding="utf-8") as f:
                questions_list = json.load(f)
                self.questions_data = {q["id"]: q for q in questions_list}

    def load_concepts(self, concepts: List[Dict[str, Any]]) -> None:
        """FR-G1: Build Directed Acyclic Graph from concepts list and FR-G2: validate."""
        self.G.clear()
        self.concepts_data = {c["id"]: c for c in concepts}
        
        for c in concepts:
            self.G.add_node(
                c["id"],
                name=c["name"],
                description=c.get("description", ""),
                difficulty=c.get("difficulty", 1),
                tier=c.get("tier", 1),
                learning_objectives=c.get("learning_objectives", []),
                resources=c.get("resources", [])
            )
            
        for c in concepts:
            for prereq in c.get("prerequisites", []):
                # Edge direction: A -> B means A is prerequisite for B
                self.G.add_edge(prereq, c["id"])
                
        self.validate_graph()

    def validate_graph(self) -> None:
        """
        FR-G2: Startup validation
        - No cycles (DAG)
        - No dangling prerequisite IDs
        - No self-edges
        - No disconnected orphan concepts (except valid root foundations)
        """
        # 1. Self loops
        self_loops = list(nx.nodes_with_selfloops(self.G))
        if self_loops:
            raise ValueError(f"Self-edges detected on nodes: {self_loops}")

        # 2. Dangling prerequisites
        for u, v in self.G.edges():
            if u not in self.concepts_data:
                raise ValueError(f"Dangling prerequisite ID: '{u}' is required by '{v}' but not defined")
            if v not in self.concepts_data:
                raise ValueError(f"Target node '{v}' not defined")

        # 3. Cycle Detection
        if not nx.is_directed_acyclic_graph(self.G):
            cycles = list(nx.simple_cycles(self.G))
            raise ValueError(f"Cycle detected in prerequisite graph: {cycles}")

        # 4. Orphan check (isolated nodes with no incoming and no outgoing edges)
        orphans = [n for n in self.G.nodes() if self.G.in_degree(n) == 0 and self.G.out_degree(n) == 0]
        if orphans and len(self.G.nodes()) > 1:
            raise ValueError(f"Orphan isolated concepts detected: {orphans}")

    def get_prerequisites(self, concept_id: str) -> List[str]:
        """Direct prerequisites (in-edges in prerequisite direction)."""
        return list(self.G.predecessors(concept_id))

    def get_dependents(self, concept_id: str) -> List[str]:
        """Direct dependents (out-edges)."""
        return list(self.G.successors(concept_id))

    def get_ancestors_with_distance(self, concept_id: str) -> Dict[str, int]:
        """
        FR-G3: Returns all ancestors (foundational prerequisites) with shortest distance.
        """
        if concept_id not in self.G:
            return {}
        
        ancestors = nx.ancestors(self.G, concept_id)
        result = {}
        for anc in ancestors:
            # Distance from ancestor to concept_id
            try:
                dist = nx.shortest_path_length(self.G, source=anc, target=concept_id)
                result[anc] = dist
            except nx.NetworkXNoPath:
                pass
        return result

    def compute_importance(self, concept_id: str) -> float:
        """
        FR-G5: Downstream descendant share:
        importance = |descendants(c)| / |total_concepts|
        """
        if concept_id not in self.G or len(self.G) == 0:
            return 0.0
        descendants = nx.descendants(self.G, concept_id)
        return len(descendants) / len(self.G)

    def get_topological_sort(self, subset_ids: Optional[List[str]] = None) -> List[str]:
        """
        FR-G4: Return valid learning order (topological sort).
        """
        if subset_ids:
            # Subgraph induced by the subset
            valid_ids = [cid for cid in subset_ids if cid in self.G]
            sub = self.G.subgraph(valid_ids)
            return list(nx.topological_sort(sub))
        return list(nx.topological_sort(self.G))

    def get_transitive_reduction(self) -> List[Tuple[str, str]]:
        """
        FR-G6: Minimal DAG edge representation for uncluttered visual layouts.
        """
        tr = nx.transitive_reduction(self.G)
        return list(tr.edges())

    def update_mastery_state(self, responses: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Bayesian belief updating per SRS Section 5.2:
        - Prior p0 = 0.50
        - Likelihood with slip s=0.10, guess g=0.20
        - Response time & distractor adjustments
        - Direct vs indirect propagation
        """
        mastery: Dict[str, Dict[str, Any]] = {}
        for cid in self.G.nodes():
            mastery[cid] = {
                "concept_id": cid,
                "p": 0.50,
                "n_direct": 0,
                "n_indirect": 0,
                "status": "insufficient",
                "blocker_score": 0.0,
                "uncertainty": 1.0
            }

        s = 0.10  # slip
        g = 0.20  # guess

        for resp in responses:
            cid = resp.get("concept_id")
            if not cid or cid not in mastery:
                continue

            correct = bool(resp.get("correct"))
            confidence = resp.get("confidence", "medium")
            response_ms = resp.get("response_ms", 1500)
            
            # Confidence weight
            w = 1.0
            if confidence == "high":
                w = 1.25 if correct else 1.35
            elif confidence == "low":
                w = 0.75

            # Latency factor (quick correct = high confidence, fast incorrect = guessing)
            if response_ms < 2000 and not correct:
                w *= 1.15

            curr_p = mastery[cid]["p"]

            # Bayesian update
            if correct:
                p_c = curr_p * (1 - s) + (1 - curr_p) * g
                post = (curr_p * (1 - s)) / (p_c if p_c > 0 else 0.001)
                new_p = curr_p + (post - curr_p) * (0.8 * w)
            else:
                p_inc = curr_p * s + (1 - curr_p) * (1 - g)
                post = (curr_p * s) / (p_inc if p_inc > 0 else 0.001)
                new_p = curr_p + (post - curr_p) * (0.9 * w)

            mastery[cid]["p"] = max(0.02, min(0.98, new_p))
            mastery[cid]["n_direct"] += 1

            # Prerequisite propagation (Section 5.2.5)
            prereqs = self.get_prerequisites(cid)
            for pr in prereqs:
                if pr in mastery:
                    if not correct:
                        # propagate down to prerequisites
                        mastery[pr]["p"] = max(0.05, mastery[pr]["p"] - (0.12 * w))
                        mastery[pr]["n_indirect"] += 1
                    else:
                        mastery[pr]["p"] = min(0.95, mastery[pr]["p"] + (0.05 * w))
                        mastery[pr]["n_indirect"] += 1

        # Classify status per SRS Section 5.3
        for cid, m in mastery.items():
            p = m["p"]
            n_direct = m["n_direct"]
            importance = self.compute_importance(cid)
            m["blocker_score"] = round((1.0 - p) * importance, 4)
            m["uncertainty"] = round(1.0 - abs(2.0 * p - 1.0), 3)

            if p >= 0.70 and n_direct >= 1:
                m["status"] = "mastered" if p >= 0.85 else "rejected"
            elif p < 0.30 and n_direct >= 2:
                m["status"] = "confirmed"
            elif p < 0.50 or m["n_indirect"] > 0:
                m["status"] = "suspected"
            else:
                m["status"] = "insufficient"

        return mastery

    def diagnose_root_gap(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        SRS Section 5.4: Root-Gap Selection using NetworkX DAG.
        Among confirmed (or suspected) gaps in the ancestors of the failed concept,
        choose the one with highest blocker_score = (1 - p) * importance.
        Ties broken by greatest depth (closest to foundational root).
        """
        mastery = self.update_mastery_state(responses)
        
        # Find concepts with failures
        failed_concepts = [r["concept_id"] for r in responses if not r.get("correct")]
        target_failed = failed_concepts[-1] if failed_concepts else "D13"

        # Find candidate ancestors using NetworkX
        ancestors_dist = self.get_ancestors_with_distance(target_failed)
        ancestor_candidates = [cid for cid in ancestors_dist.keys() if mastery[cid]["status"] in ("confirmed", "suspected")]

        if not ancestor_candidates:
            # If no ancestor flagged, consider target failed concept itself
            root_gap_id = target_failed
            evidence_path = [target_failed]
        else:
            # Score each candidate by blocker_score, then by distance to target (depth)
            def score_candidate(cid: str) -> Tuple[float, int]:
                b_score = mastery[cid]["blocker_score"]
                depth = ancestors_dist.get(cid, 0)
                return (b_score, depth)

            root_gap_id = max(ancestor_candidates, key=score_candidate)
            # Find shortest path from root gap to target concept using NetworkX
            try:
                evidence_path = nx.shortest_path(self.G, source=root_gap_id, target=target_failed)
            except nx.NetworkXNoPath:
                evidence_path = [root_gap_id, target_failed]

        root_name = self.concepts_data.get(root_gap_id, {}).get("name", root_gap_id)
        target_name = self.concepts_data.get(target_failed, {}).get("name", target_failed)

        explanation = (
            f"Failure on '{target_name}' was traced via prerequisite graph to foundational concept "
            f"'{root_name}'. Resolving '{root_name}' unlocks {len(nx.descendants(self.G, root_gap_id))} "
            f"downstream concepts in the DBMS curriculum."
        )

        return {
            "target_failed_concept": target_failed,
            "root_gap_id": root_gap_id,
            "root_gap_name": root_name,
            "evidence_path": evidence_path,
            "mastery_map": mastery,
            "confirmed_gaps": [cid for cid, m in mastery.items() if m["status"] == "confirmed"],
            "suspected_gaps": [cid for cid, m in mastery.items() if m["status"] == "suspected"],
            "mastered": [cid for cid, m in mastery.items() if m["status"] in ("mastered", "rejected")],
            "explanation": explanation
        }

    def generate_learning_roadmap(self, gap_ids: List[str]) -> List[Dict[str, Any]]:
        """
        FR-G4: Topologically sorted learning path for remediating gaps.
        Includes all required prerequisite ancestors.
        """
        # Expand gap_ids to include their unmastered ancestors
        all_remediation_nodes: Set[str] = set(gap_ids)
        for gid in gap_ids:
            if gid in self.G:
                all_remediation_nodes.update(nx.ancestors(self.G, gid))

        # Perform NetworkX topological sort
        sorted_ids = self.get_topological_sort(list(all_remediation_nodes))
        
        steps = []
        for idx, cid in enumerate(sorted_ids, 1):
            c_info = self.concepts_data.get(cid, {})
            prereqs = self.get_prerequisites(cid)
            prereq_names = [self.concepts_data.get(p, {}).get("name", p) for p in prereqs]
            
            rationale = (
                f"Foundational requirement for {c_info.get('name', cid)}."
                if not prereqs else
                f"Builds directly upon completed foundations: {', '.join(prereq_names)}."
            )

            steps.append({
                "position": idx,
                "concept_id": cid,
                "concept_name": c_info.get("name", cid),
                "prerequisites": prereqs,
                "rationale": rationale,
                "estimated_mins": 15 + c_info.get("difficulty", 1) * 5,
                "resources": c_info.get("resources", [])
            })

        return steps
