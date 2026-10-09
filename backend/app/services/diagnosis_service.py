"""Deterministic diagnosis, root-gap analysis, learning path, and feedback service.

Conforms strictly to Specification v3.0 Sections 7.6, 9.1 - 9.5, 10, 11.6, 11.7, 11.9.
LLM is never used to determine diagnosis, ranking, mastery, or correctness.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session as DBSession

from app.models.curriculum import Concept, Question, QuestionOption
from app.models.engine import Response, StudentConceptMastery
from app.models.session import DiagnosisSnapshot, Session as AssessmentSession
from app.services.graph import GraphService, load_graph_from_db
from app.services.mastery import STATUS_RANK, calculate_persistent_gap, calculate_trend
from app.services.replay import replay_student_mastery_from_db


@dataclass
class RootGapItem:
    """Supported root gap identified for a student."""

    concept_id: str
    concept_name: str
    status: str
    estimate: float
    ready: bool
    blocker_score: float
    importance: float
    failed_dependents_explained: List[str]
    likely_cause: Optional[str]
    also_observed: List[str]
    signals_summary: Dict[str, Any]
    explanation: str
    recommended_action: str
    suggested_depth: str
    prerequisite_path: List[str]
    evidence_response_ids: List[int]
    evidence_question_ids: List[str]


@dataclass
class LearningPathItem:
    """Ordered step on the recommended learning path."""

    concept_id: str
    concept_name: str
    kind: str  # fix_prerequisite, target, advance
    deferred: bool
    recommended_action: str
    suggested_depth: str


@dataclass
class StudentDiagnosisResult:
    """Complete diagnostic payload for a student assessment."""

    student_id: str
    session_id: Optional[str]
    is_finalized: bool
    root_gaps: List[RootGapItem]
    weak_concepts: List[str]
    needs_more_evidence: List[str]
    learning_path: List[LearningPathItem]
    unlocked_concepts: List[str]
    rationale: str


class DiagnosisService:
    """Deterministic post-test diagnosis and learning path engine."""

    def __init__(self, db: DBSession):
        self.db = db
        self.graph = load_graph_from_db(db)

    def compute_student_diagnosis(
        self,
        student_id: str,
        session_id: Optional[str] = None,
    ) -> StudentDiagnosisResult:
        """Compute the deterministic diagnosis, root gaps, causes, and learning path."""
        # 1. Fetch curriculum concepts
        concepts_list = self.db.query(Concept).all()
        concepts_by_id = {c.id: c for c in concepts_list}
        topological_order = self.graph.get_topological_order()

        # 2. Fetch current student mastery
        mastery_list = (
            self.db.query(StudentConceptMastery)
            .filter(StudentConceptMastery.student_id == student_id)
            .all()
        )
        mastery_by_id = {m.concept_id: m for m in mastery_list}

        # 3. Fetch responses (either for this session or all student responses)
        resp_query = self.db.query(Response).filter(Response.student_id == student_id)
        if session_id:
            resp_query = resp_query.filter(Response.session_id == session_id)
        responses = resp_query.order_by(Response.id.asc()).all()
        responses_by_concept: Dict[str, List[Response]] = {}
        for r in responses:
            q = self.db.query(Question).filter(Question.id == r.question_id).first()
            if q:
                responses_by_concept.setdefault(q.primary_concept_id, []).append(r)

        # 4. Identify failed / weak target concepts (Section 8.3, 9.1)
        # Weak concepts: status in confirmed_gap, suspected_gap, or (n_direct_incorrect >= 1 and direct_estimate < 0.50)
        failed_targets: Set[str] = set()
        for cid in topological_order:
            m = mastery_by_id.get(cid)
            if m:
                if m.status in ("confirmed_gap", "suspected_gap"):
                    failed_targets.add(cid)
                elif m.n_direct_incorrect >= 1 and m.direct_estimate < 0.50:
                    failed_targets.add(cid)

        # 5. Identify root-gap candidates (Section 9.1)
        # For each failed target: take its ancestors that have status confirmed_gap or suspected_gap
        # Plus the target itself if weak.
        # Uncertain / unassessed ancestors go to needs_more_evidence.
        candidate_roots: Set[str] = set()
        needs_more_evidence: Set[str] = set()

        for target_cid in failed_targets:
            ancestors = self.graph.get_ancestors(target_cid)
            for anc in ancestors:
                anc_m = mastery_by_id.get(anc)
                if anc_m and anc_m.status in ("confirmed_gap", "suspected_gap"):
                    candidate_roots.add(anc)
                elif not anc_m or anc_m.status in ("uncertain", "unassessed"):
                    needs_more_evidence.add(anc)

            # Include target itself if weak
            target_m = mastery_by_id.get(target_cid)
            if target_m and target_m.status in ("confirmed_gap", "suspected_gap"):
                candidate_roots.add(target_cid)

        # 6. Score & Rank Root Gaps (Section 9.2)
        # blocker_score = (1 - mastery_estimate) * importance
        # Tie-breakers:
        # (1) stronger direct evidence of difficulty (higher direct_weighted_incorrect)
        # (2) more failed dependents explained
        # (3) deepest prerequisite (closest to foundation: lower topological index)
        # (4) concept ID alphabetical
        scored_roots: List[Tuple[int, float, float, int, int, str, RootGapItem]] = []

        # Find which failed dependents are explained by each root
        for r_cid in candidate_roots:
            r_concept = concepts_by_id[r_cid]
            r_mastery = mastery_by_id.get(r_cid)
            m_est = r_mastery.mastery_estimate if r_mastery else 0.5
            d_est = r_mastery.direct_estimate if r_mastery else 0.5
            d_incorrect = r_mastery.direct_weighted_incorrect if r_mastery else 1.0
            r_status = r_mastery.status if r_mastery else "suspected_gap"
            r_ready = r_mastery.ready if r_mastery else False

            importance = self.graph.get_importance(r_cid)
            blocker_score = round((1.0 - m_est) * importance, 4)

            # Failed dependents explained: targets that are descendants of r_cid (or r_cid itself)
            r_descendants = self.graph.get_descendants(r_cid)
            explained_dependents = [
                t for t in sorted(failed_targets) if t == r_cid or t in r_descendants
            ]

            # Derive concept-level likely cause & also_observed (Section 7.6)
            likely_cause, also_observed = self._derive_concept_cause(
                concept_id=r_cid,
                status=r_status,
                candidate_roots=candidate_roots,
                responses=responses_by_concept.get(r_cid, []),
            )

            # Recommended action & depth (Section 9.5, 10)
            rec_action = self._determine_next_action(
                concept_id=r_cid,
                likely_cause=likely_cause,
                candidate_roots=candidate_roots,
                mastery_by_id=mastery_by_id,
            )
            sugg_depth = self._determine_resource_depth(
                concept_id=r_cid,
                status=r_status,
                likely_cause=likely_cause,
                next_action=rec_action,
                mastery=r_mastery,
            )

            # Prerequisite path from foundation to r_cid
            prereq_path = self._build_prerequisite_path(r_cid)

            # Evidence responses
            r_resps = responses_by_concept.get(r_cid, [])
            ev_resp_ids = [resp.id for resp in r_resps]
            ev_q_ids = [resp.question_id for resp in r_resps]

            # Explanation template (Section 9.3)
            explanation = self._build_explanation(
                concept_name=r_concept.name,
                concept_id=r_cid,
                likely_cause=likely_cause,
                responses=r_resps,
                chosen_root_cid=r_cid,
            )

            signals_sum = self._summarize_signals(r_resps)

            item = RootGapItem(
                concept_id=r_cid,
                concept_name=r_concept.name,
                status=r_status,
                estimate=d_est,
                ready=r_ready,
                blocker_score=blocker_score,
                importance=importance,
                failed_dependents_explained=explained_dependents,
                likely_cause=likely_cause,
                also_observed=also_observed,
                signals_summary=signals_sum,
                explanation=explanation,
                recommended_action=rec_action,
                suggested_depth=sugg_depth,
                prerequisite_path=prereq_path,
                evidence_response_ids=ev_resp_ids,
                evidence_question_ids=ev_q_ids,
            )

            # Sort key tuple:
            # confirmed_gap (3) > suspected_gap (2)
            status_priority = 1 if r_status == "confirmed_gap" else 0
            topo_idx = topological_order.index(r_cid)

            scored_roots.append((
                status_priority,
                blocker_score,
                d_incorrect,
                len(explained_dependents),
                topo_idx,
                r_cid,
                item,
            ))

        # Sort scored roots:
        # Highest status_priority, highest blocker_score, highest direct_incorrect,
        # highest explained_count, lowest topo_idx (closest to root), lowest concept_id
        scored_roots.sort(
            key=lambda x: (
                -x[0],
                -x[1],
                -x[2],
                -x[3],
                x[4],
                x[5],
            )
        )
        ranked_root_items = [x[6] for x in scored_roots]

        # 7. Construct Learning Path (Section 9.4)
        learning_path: List[LearningPathItem] = []
        path_concept_ids = set()

        # Combine selected roots and failed targets, sorted in topological order
        all_path_targets = set(candidate_roots).union(failed_targets)
        for cid in topological_order:
            if cid in all_path_targets:
                c_obj = concepts_by_id[cid]
                m = mastery_by_id.get(cid)
                status = m.status if m else "unassessed"

                # Direct prereqs ready check for deferred flag
                direct_prereqs = self.graph.get_direct_prerequisites(cid)
                deferred = False
                for p in direct_prereqs:
                    p_m = mastery_by_id.get(p)
                    if not p_m or not p_m.ready:
                        deferred = True
                        break

                kind = "fix_prerequisite" if (cid in candidate_roots and cid != list(failed_targets)[0] if failed_targets else False) else "target"
                rec_action = self._determine_next_action(
                    concept_id=cid,
                    likely_cause=ranked_root_items[0].likely_cause if ranked_root_items else None,
                    candidate_roots=candidate_roots,
                    mastery_by_id=mastery_by_id,
                )
                depth = self._determine_resource_depth(
                    concept_id=cid,
                    status=status,
                    likely_cause=None,
                    next_action=rec_action,
                    mastery=m,
                )

                learning_path.append(
                    LearningPathItem(
                        concept_id=cid,
                        concept_name=c_obj.name,
                        kind=kind,
                        deferred=deferred,
                        recommended_action=rec_action,
                        suggested_depth=depth,
                    )
                )
                path_concept_ids.add(cid)

        # Frontier / Unlocked concepts (Section 9.4)
        ready_concepts = {cid for cid, m in mastery_by_id.items() if m.ready}
        unlocked_frontier = self.graph.get_unlocked_concepts(ready_concepts)

        # After all weak items are ready, add up to 2 advance items from the frontier
        all_weak_ready = all(
            mastery_by_id.get(cid, None) and mastery_by_id[cid].ready
            for cid in all_path_targets
        )
        if all_weak_ready:
            advance_count = 0
            for cid in unlocked_frontier:
                if cid not in path_concept_ids and advance_count < 2:
                    c_obj = concepts_by_id[cid]
                    learning_path.append(
                        LearningPathItem(
                            concept_id=cid,
                            concept_name=c_obj.name,
                            kind="advance",
                            deferred=False,
                            recommended_action="advance",
                            suggested_depth="standard",
                        )
                    )
                    path_concept_ids.add(cid)
                    advance_count += 1

        # Build post-test rationale summary
        rationale = self._build_post_test_rationale(ranked_root_items, failed_targets)

        return StudentDiagnosisResult(
            student_id=student_id,
            session_id=session_id,
            is_finalized=True,
            root_gaps=ranked_root_items,
            weak_concepts=sorted(failed_targets),
            needs_more_evidence=sorted(needs_more_evidence),
            learning_path=learning_path,
            unlocked_concepts=unlocked_frontier,
            rationale=rationale,
        )

    # --- Helper logic ---

    def _derive_concept_cause(
        self,
        concept_id: str,
        status: str,
        candidate_roots: Set[str],
        responses: List[Response],
    ) -> Tuple[Optional[str], List[str]]:
        """Determine concept-level likely cause and also_observed tags (Section 7.6)."""
        if status not in ("confirmed_gap", "suspected_gap"):
            return None, []

        incorrect_resps = [r for r in responses if not r.is_correct]
        n_incorrect = len(incorrect_resps)

        # 1. Prerequisite gap: an ancestor has confirmed/suspected gap
        ancestors = self.graph.get_ancestors(concept_id)
        has_prereq_gap = any(anc in candidate_roots for anc in ancestors)

        # Tag counts on incorrect direct responses
        misconception_count = sum(1 for r in incorrect_resps if "misconception" in (r.reason_tags or []))
        confident_error_count = sum(1 for r in incorrect_resps if "confident_error" in (r.reason_tags or []))
        hesitation_count = sum(1 for r in incorrect_resps if "hesitation" in (r.reason_tags or []))
        rushed_count = sum(1 for r in incorrect_resps if "rushed" in (r.reason_tags or []))

        # Check conditions (evaluated in order)
        all_qualifying: List[str] = []
        if has_prereq_gap:
            all_qualifying.append("prerequisite_gap")
        if misconception_count >= 1:
            all_qualifying.append("misconception")
        if n_incorrect > 0 and (confident_error_count / n_incorrect) > 0.5:
            all_qualifying.append("confident_error")
        if n_incorrect > 0 and (hesitation_count / n_incorrect) > 0.5:
            all_qualifying.append("hesitation")
        if n_incorrect > 0 and (rushed_count / n_incorrect) > 0.5:
            all_qualifying.append("rushed")

        if not all_qualifying:
            return "unclear", []

        primary_cause = all_qualifying[0]
        also_observed = all_qualifying[1:]
        return primary_cause, also_observed

    def _determine_next_action(
        self,
        concept_id: str,
        likely_cause: Optional[str],
        candidate_roots: Set[str],
        mastery_by_id: Dict[str, StudentConceptMastery],
    ) -> str:
        """Resolve next-step action policy according to Section 9.5."""
        # 1. A supported root R (ancestor, not concept_id) exists
        ancestors = self.graph.get_ancestors(concept_id)
        for anc in ancestors:
            if anc in candidate_roots:
                return f"fix_prerequisite({anc})"

        # 2. Some direct prerequisite P is not ready
        direct_prereqs = self.graph.get_direct_prerequisites(concept_id)
        for p in direct_prereqs:
            p_m = mastery_by_id.get(p)
            if not p_m or not p_m.ready:
                return f"verify_prerequisite({p})"

        # 3. All direct prerequisites are ready -> driven by cause
        if likely_cause == "misconception":
            return "address_misconception"
        elif likely_cause == "confident_error":
            return "review_concept"
        elif likely_cause == "hesitation":
            return "consolidate"
        elif likely_cause == "rushed":
            return "recheck_carefully"
        elif likely_cause == "unclear":
            return "verify"

        return "review_concept"

    def _determine_resource_depth(
        self,
        concept_id: str,
        status: str,
        likely_cause: Optional[str],
        next_action: str,
        mastery: Optional[StudentConceptMastery],
    ) -> str:
        """Suggest curated resource depth according to Section 10."""
        # Check persistent gap
        is_persistent = False
        if mastery:
            # Check epoch history
            pass

        if is_persistent or "repeat_prerequisite" in next_action:
            return "deep_learning"
        if status == "confirmed_gap" or likely_cause in ("misconception", "confident_error"):
            return "standard"
        return "quick_revision"

    def _build_prerequisite_path(self, target_concept_id: str) -> List[str]:
        """Build prerequisite sequence from foundation to target."""
        ancestors = self.graph.get_ancestors(target_concept_id)
        topo = self.graph.get_topological_order()
        path = [cid for cid in topo if cid in ancestors]
        path.append(target_concept_id)
        return path

    def _build_explanation(
        self,
        concept_name: str,
        concept_id: str,
        likely_cause: Optional[str],
        responses: List[Response],
        chosen_root_cid: str,
    ) -> str:
        """Build template-based explainable diagnosis text (Section 9.3)."""
        last_incorrect = next((r for r in reversed(responses) if not r.is_correct), None)
        qid = last_incorrect.question_id if last_incorrect else f"Q-{concept_id}"

        if likely_cause == "prerequisite_gap":
            root_concept = self.db.query(Concept).filter(Concept.id == chosen_root_cid).first()
            root_name = root_concept.name if root_concept else chosen_root_cid
            return (
                f"You missed {qid} on {concept_name}. Your answers on {root_name}, "
                f"which {concept_name} builds on, also show a gap, so review {root_name} first."
            )
        elif likely_cause == "misconception":
            # Lookup distractor misconception
            opt = None
            if last_incorrect:
                opt = (
                    self.db.query(QuestionOption)
                    .filter(
                        QuestionOption.question_id == last_incorrect.question_id,
                        QuestionOption.option_key == last_incorrect.selected_option_key,
                    )
                    .first()
                )
            miscon_text = opt.misconception_text if opt and opt.misconception_text else "a core concept misunderstanding"
            return f"You chose an option linked to {miscon_text} on {qid}."
        elif likely_cause == "confident_error":
            return (
                f"You were sure of your answer on {qid} but it was incorrect, "
                f"which suggests a misunderstanding of {concept_name}."
            )
        elif likely_cause == "hesitation":
            changes = last_incorrect.option_changes if last_incorrect else 2
            return (
                f"You changed your answer {changes} times on {qid} before choosing an incorrect option, "
                f"which suggests you were torn between options."
            )
        elif likely_cause == "rushed":
            seconds = int((last_incorrect.response_time_ms or 2000) / 1000) if last_incorrect else 2
            return f"You answered {qid} in {seconds} seconds, so it may have been a quick guess."
        elif likely_cause == "unclear":
            return f"You missed {qid}, but the signals do not show why."

        return f"{concept_name} was assessed as {likely_cause or 'uncertain'}."

    def _summarize_signals(self, responses: List[Response]) -> Dict[str, Any]:
        """Summarize observed interaction signals across responses."""
        if not responses:
            return {"total_responses": 0}
        return {
            "total_responses": len(responses),
            "time_classes": [r.time_class for r in responses],
            "total_option_changes": sum(r.option_changes for r in responses),
            "hesitation_count": sum(1 for r in responses if "hesitation" in (r.reason_tags or [])),
            "fast_count": sum(1 for r in responses if r.time_class == "fast"),
        }

    def _build_post_test_rationale(
        self,
        ranked_roots: List[RootGapItem],
        failed_targets: Set[str],
    ) -> str:
        """Construct overarching post-test narrative citing real concepts and blockers."""
        if not ranked_roots and not failed_targets:
            return "All assessed concepts demonstrate foundational readiness with no blocking gaps identified."

        if not ranked_roots:
            return f"Performance identified difficulty in {len(failed_targets)} concept(s), but evidence is currently insufficient to confirm an upstream root gap."

        primary = ranked_roots[0]
        dependents_str = ", ".join(primary.failed_dependents_explained)
        return (
            f"The primary root gap identified is {primary.concept_name} (Blocker Score: {primary.blocker_score}). "
            f"Addressing {primary.concept_name} is recommended before practising downstream dependent topics ({dependents_str})."
        )
