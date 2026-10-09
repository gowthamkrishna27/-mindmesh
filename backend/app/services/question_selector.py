"""Adaptive question selection engine for student diagnostic assessments.

Conforms strictly to Specification v3.0 Sections 5.3, 8.1 - 8.3.
LLM is never used to select questions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from app.core.settings_rules import (
    MAX_DIAGNOSTIC_QUESTIONS_PER_CONCEPT,
    MAX_DIAGNOSTIC_SESSION_QUESTIONS,
    PREREQUISITE_FAILED_BONUS,
    RANK_WEIGHT_C,
    RANK_WEIGHT_I,
    RANK_WEIGHT_S,
    RANK_WEIGHT_U,
)
from app.models.curriculum import Concept, Question
from app.models.engine import Response, StudentConceptMastery
from app.models.session import SelectionLog, SessionQuestionIssue
from app.services.graph import GraphService


# Baseline non-root branch priority order (Section 8.1)
# 1. Foundation: D02 (highest-importance non-root concept)
# 2. Design: D03 (highest-importance non-root concept)
# 3. SQL: D08 (highest-importance non-root concept)
# 4. Root unsampled overall: D01
BASELINE_CONCEPT_ORDER: List[str] = ["D02", "D03", "D08", "D01"]


@dataclass
class SelectionResult:
    """Outcome of an adaptive question selection step."""

    question: Optional[Question]
    reason: str
    candidate_scores: Dict[str, Any]
    exhausted: bool = False


class QuestionSelector:
    """Deterministic adaptive question selector."""

    def __init__(self, db: Session, graph_service: GraphService):
        self.db = db
        self.graph = graph_service

    def select_next_diagnostic_question(
        self,
        session_id: str,
        student_id: str,
    ) -> SelectionResult:
        """Select the next eligible question for a diagnostic session.

        Follows:
        1. Check session limit (12 answers max).
        2. Baseline coverage (up to 4): D02, D03, D08, D01.
        3. Targeted prerequisite probe: most recently failed concept's direct unasked prerequisite.
        4. Ranked selection formula (Section 8.3).
        5. Return question or exhausted status.
        """
        # 1. Fetch questions already issued in this session
        issued_issues = (
            self.db.query(SessionQuestionIssue)
            .filter(SessionQuestionIssue.session_id == session_id)
            .all()
        )
        issued_qids: Set[str] = {issue.question_id for issue in issued_issues}

        if len(issued_qids) >= MAX_DIAGNOSTIC_SESSION_QUESTIONS:
            return SelectionResult(
                question=None,
                reason="session_limit_reached",
                candidate_scores={},
                exhausted=True,
            )

        # Count questions issued per concept in this session
        all_questions = self.db.query(Question).all()
        questions_by_id = {q.id: q for q in all_questions}
        concept_issued_counts: Dict[str, int] = {}
        issued_families: Set[str] = set()

        for qid in issued_qids:
            q = questions_by_id.get(qid)
            if q:
                cid = q.primary_concept_id
                concept_issued_counts[cid] = concept_issued_counts.get(cid, 0) + 1
                issued_families.add(q.question_family)

        # Fetch current mastery states for student
        mastery_records = (
            self.db.query(StudentConceptMastery)
            .filter(StudentConceptMastery.student_id == student_id)
            .all()
        )
        mastery_by_concept = {m.concept_id: m for m in mastery_records}

        # Fetch concepts metadata
        concepts_list = self.db.query(Concept).all()
        concepts_by_id = {c.id: c for c in concepts_list}
        all_concept_ids = set(concepts_by_id.keys())

        # Branches that have had at least one question issued this session
        branches_with_questions: Set[str] = set()
        for cid, count in concept_issued_counts.items():
            if count > 0 and cid in concepts_by_id:
                branches_with_questions.add(concepts_by_id[cid].branch)

        # Helper to get eligible questions for a concept
        def get_eligible_questions(concept_id: str) -> List[Question]:
            if concept_issued_counts.get(concept_id, 0) >= MAX_DIAGNOSTIC_QUESTIONS_PER_CONCEPT:
                return []

            candidates = [
                q
                for q in all_questions
                if q.primary_concept_id == concept_id
                and q.review_status == "reviewed"
                and q.use_for_diagnosis
                and q.id not in issued_qids
            ]

            # Reserve held-out retest items if standard diagnostic items exist (Section 5.3, 8.2)
            non_retest = [q for q in candidates if not q.use_for_retest]
            if non_retest:
                return non_retest
            # Held-out items should not be used in diagnosis if avoidable
            return candidates

        # 2. Phase 1: Baseline Coverage (Section 8.1)
        for baseline_cid in BASELINE_CONCEPT_ORDER:
            if baseline_cid in all_concept_ids:
                if concept_issued_counts.get(baseline_cid, 0) == 0:
                    eligible_qs = get_eligible_questions(baseline_cid)
                    if eligible_qs:
                        chosen_q = self._pick_best_question(eligible_qs, issued_families)
                        return SelectionResult(
                            question=chosen_q,
                            reason=f"baseline_coverage:{baseline_cid}",
                            candidate_scores={baseline_cid: {"phase": "baseline"}},
                        )

        # 3. Phase 2: Prerequisite Probe (Section 8.1)
        # Fetch responses in this session in reverse order
        session_responses = (
            self.db.query(Response)
            .filter(Response.session_id == session_id)
            .order_by(Response.id.desc())
            .all()
        )

        # Previously probed (T, P) pairs in this session from SelectionLog
        probed_logs = (
            self.db.query(SelectionLog)
            .filter(
                SelectionLog.session_id == session_id,
                SelectionLog.reason.startswith("prerequisite_probe:"),
            )
            .all()
        )
        probed_pairs: Set[Tuple[str, str]] = set()
        for log in probed_logs:
            # log.reason format: "prerequisite_probe:T={target},P={prereq}"
            try:
                parts = log.reason.split(":")[-1].split(",")
                t_val = parts[0].split("=")[-1].strip()
                p_val = parts[1].split("=")[-1].strip()
                probed_pairs.add((t_val, p_val))
            except Exception:
                pass

        # Identify failed concepts: n_direct_incorrect >= 1 and direct_estimate < 0.50
        failed_concepts_seen: Set[str] = set()
        for resp in session_responses:
            resp_q = questions_by_id.get(resp.question_id)
            if not resp_q:
                continue
            target_cid = resp_q.primary_concept_id
            if target_cid in failed_concepts_seen:
                continue

            m = mastery_by_concept.get(target_cid)
            if m and m.n_direct_incorrect >= 1 and m.direct_estimate < 0.50:
                failed_concepts_seen.add(target_cid)

                # Direct prerequisites of target_cid
                direct_prereqs = sorted(self.graph.get_direct_prerequisites(target_cid))
                # Sort candidate prerequisites: larger importance first, then ID (Section 8.1)
                direct_prereqs.sort(
                    key=lambda p_id: (-self.graph.get_importance(p_id), p_id)
                )

                for prereq_id in direct_prereqs:
                    # Check: no direct question yet this session, not yet probed for this pair, eligible items exist
                    if concept_issued_counts.get(prereq_id, 0) == 0:
                        if (target_cid, prereq_id) not in probed_pairs:
                            eligible_qs = get_eligible_questions(prereq_id)
                            if eligible_qs:
                                chosen_q = self._pick_best_question(eligible_qs, issued_families)
                                return SelectionResult(
                                    question=chosen_q,
                                    reason=f"prerequisite_probe:T={target_cid},P={prereq_id}",
                                    candidate_scores={
                                        prereq_id: {
                                            "phase": "prerequisite_probe",
                                            "target_failed_concept": target_cid,
                                        }
                                    },
                                )

        # 4. Phase 3: Ranked Selection Formula (Section 8.3)
        # Find all direct prerequisites of all failed concepts
        direct_prereqs_of_failed: Set[str] = set()
        for f_cid in failed_concepts_seen:
            direct_prereqs_of_failed.update(self.graph.get_direct_prerequisites(f_cid))

        candidate_scores: Dict[str, Any] = {}
        ranked_candidates: List[Tuple[float, Tuple[Any, ...], str, Question]] = []

        total_graph_concepts = len(self.graph.graph.nodes)
        denominator_n = max(1, total_graph_concepts - 1)

        for cid in sorted(all_concept_ids):
            eligible_qs = get_eligible_questions(cid)
            if not eligible_qs:
                continue

            c_obj = concepts_by_id[cid]
            m_state = mastery_by_concept.get(cid)

            # Mastery estimate (blended) defaults to 0.5
            mastery_est = m_state.mastery_estimate if m_state else 0.5
            weighted_incorrect = m_state.weighted_incorrect if m_state else 1.0
            direct_weighted_incorrect = m_state.direct_weighted_incorrect if m_state else 1.0

            # U = 1 - abs(2 * mastery_estimate - 1)
            U = 1.0 - abs(2.0 * mastery_est - 1.0)

            # I = descendant_count(concept) / (n_concepts - 1)
            I = self.graph.get_importance(cid)

            # S = min(1, (weighted_incorrect - 1) / 3) + 0.25 * [direct prereq of failed concept]
            is_prereq_of_failed = cid in direct_prereqs_of_failed
            struggle_base = max(0.0, (weighted_incorrect - 1.0) / 3.0)
            bonus = PREREQUISITE_FAILED_BONUS if is_prereq_of_failed else 0.0
            S = min(1.0, struggle_base + bonus)

            # C = 1 if the concept's branch has no question yet this session, else 0
            C = 1.0 if c_obj.branch not in branches_with_questions else 0.0

            rank_score = (
                RANK_WEIGHT_U * U
                + RANK_WEIGHT_I * I
                + RANK_WEIGHT_S * S
                + RANK_WEIGHT_C * C
            )

            candidate_scores[cid] = {
                "U": round(U, 4),
                "I": round(I, 4),
                "S": round(S, 4),
                "C": round(C, 4),
                "rank_score": round(rank_score, 4),
            }

            best_q = self._pick_best_question(eligible_qs, issued_families)

            # Tie-breakers (Section 8.3):
            # (1) prerequisite of a failed concept (True > False)
            # (2) stronger direct evidence of difficulty (higher direct_weighted_incorrect)
            # (3) concept not yet asked (True > False)
            # (4) stable concept ID order (alphabetical, handled by negative tuple or string)
            not_yet_asked = concept_issued_counts.get(cid, 0) == 0
            tie_breaker = (
                1 if is_prereq_of_failed else 0,
                direct_weighted_incorrect,
                1 if not_yet_asked else 0,
                # For string min-order, we can use a reverse comparator or sort key
            )

            ranked_candidates.append((rank_score, tie_breaker, cid, best_q))

        if not ranked_candidates:
            return SelectionResult(
                question=None,
                reason="question_bank_exhausted",
                candidate_scores={},
                exhausted=True,
            )

        # Sort ranked candidates:
        # Highest rank_score, then tie-breakers (1, 2, 3 descending), then cid ascending
        ranked_candidates.sort(
            key=lambda item: (
                -item[0],           # rank_score descending
                -item[1][0],        # prereq of failed descending
                -item[1][1],        # direct difficulty descending
                -item[1][2],        # not yet asked descending
                item[2],            # concept ID ascending
            )
        )

        winning_cid = ranked_candidates[0][2]
        winning_q = ranked_candidates[0][3]

        return SelectionResult(
            question=winning_q,
            reason="ranked_selection",
            candidate_scores=candidate_scores,
        )

    def _pick_best_question(
        self,
        questions: List[Question],
        issued_families: Set[str],
    ) -> Question:
        """Pick the best question within a chosen concept.

        Prefers an unused question family in this session, breaking ties by question ID.
        """
        # Prefer questions with family not yet in issued_families
        unused_family_qs = [q for q in questions if q.question_family not in issued_families]
        if unused_family_qs:
            unused_family_qs.sort(key=lambda q: q.id)
            return unused_family_qs[0]

        # Otherwise sort by question ID
        sorted_qs = sorted(questions, key=lambda q: q.id)
        return sorted_qs[0]
