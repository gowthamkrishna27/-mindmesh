"""Curriculum Seed & Validation Pipeline.

Usage:
    python -m app.db.seed [--data-dir PATH] [--dry-run]
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.errors import AppError
from app.db.session import SessionLocal
from app.models.curriculum import (
    Concept,
    PrerequisiteEdge,
    Question,
    QuestionHint,
    QuestionOption,
    Resource,
)
from app.services.graph import GraphService, GraphValidationError


class SeedValidationError(AppError):
    """Raised when curriculum content fails educational or schema validation."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message=message, code="SEED_VALIDATION_ERROR", status_code=422, details=details)


def load_json_file(file_path: str) -> Any:
    """Load and parse JSON file from disk with clean error handling."""
    if not os.path.exists(file_path):
        raise SeedValidationError(f"Required seed file not found: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise SeedValidationError(f"Invalid JSON format in {file_path}: {exc}") from exc


def validate_curriculum_data(
    concepts_raw: List[Dict[str, Any]],
    questions_raw: List[Dict[str, Any]],
    resources_raw: List[Dict[str, Any]],
) -> Tuple[GraphService, Dict[str, Any]]:
    """Strict pre-insert validation of concepts, graph, questions, and resources.

    Returns:
        (GraphService, summary_statistics)
    """
    errors: List[str] = []

    # --- 1. Validate Concepts ---
    concept_map: Dict[str, Dict[str, Any]] = {}
    edges_list: List[Tuple[str, str]] = []

    for idx, c in enumerate(concepts_raw):
        cid = c.get("id")
        if not cid:
            errors.append(f"Concept at index {idx} missing 'id'.")
            continue
        if cid in concept_map:
            errors.append(f"Duplicate concept ID: '{cid}'.")
        concept_map[cid] = c

        for field in ["name", "description", "learning_objective", "branch"]:
            if not c.get(field):
                errors.append(f"Concept '{cid}' missing required field '{field}'.")

        for prereq in c.get("prerequisites", []):
            edges_list.append((prereq, cid))

    # Graph DAG validation
    try:
        graph_service = GraphService(
            concept_ids=list(concept_map.keys()),
            edges=edges_list,
            validate_expected=True,
        )
    except GraphValidationError as exc:
        errors.append(f"Graph validation failed: {exc.message}")
        graph_service = None

    # --- 2. Validate Questions ---
    valid_concept_ids = set(concept_map.keys())
    valid_families = {"recognition", "interpretation", "application", "error_analysis"}
    seen_question_ids: Set[str] = set()

    concept_question_counts: Dict[str, Dict[str, int]] = {
        cid: {"total": 0, "diagnostic": 0, "retest": 0, "reviewed": 0, "draft": 0}
        for cid in valid_concept_ids
    }
    concept_diagnostic_families: Dict[str, Set[str]] = {cid: set() for cid in valid_concept_ids}
    concept_retest_families: Dict[str, Set[str]] = {cid: set() for cid in valid_concept_ids}
    concept_diagnostic_variants: Dict[str, Set[str]] = {cid: set() for cid in valid_concept_ids}
    concept_retest_variants: Dict[str, Set[str]] = {cid: set() for cid in valid_concept_ids}

    for idx, q in enumerate(questions_raw):
        qid = q.get("id")
        if not qid:
            errors.append(f"Question at index {idx} missing 'id'.")
            continue
        if qid in seen_question_ids:
            errors.append(f"Duplicate question ID: '{qid}'.")
        seen_question_ids.add(qid)

        primary_cid = q.get("primary_concept_id")
        if primary_cid not in valid_concept_ids:
            errors.append(f"Question '{qid}' references non-existent primary_concept_id '{primary_cid}'.")

        family = q.get("question_family")
        if family not in valid_families:
            errors.append(f"Question '{qid}' has invalid question_family '{family}'. Expected one of {valid_families}.")

        diff = q.get("difficulty")
        if not isinstance(diff, int) or diff < 1 or diff > 5:
            errors.append(f"Question '{qid}' difficulty '{diff}' must be an integer between 1 and 5.")

        expected_time = q.get("expected_time_s")
        if not isinstance(expected_time, (int, float)) or expected_time <= 0:
            errors.append(f"Question '{qid}' expected_time_s must be a positive number.")

        if not q.get("prompt"):
            errors.append(f"Question '{qid}' missing prompt text.")
        if not q.get("explanation"):
            errors.append(f"Question '{qid}' missing explanation text.")

        variant_group = q.get("variant_group")
        if not variant_group:
            errors.append(f"Question '{qid}' missing variant_group.")

        # Options validation
        options = q.get("options", [])
        if len(options) != 4:
            errors.append(f"Question '{qid}' must have exactly 4 options; found {len(options)}.")

        correct_count = 0
        seen_keys: Set[str] = set()
        for opt in options:
            okey = opt.get("option_key")
            if not okey:
                errors.append(f"Question '{qid}' contains option missing option_key.")
            if okey in seen_keys:
                errors.append(f"Question '{qid}' has duplicate option key '{okey}'.")
            seen_keys.add(okey)

            if opt.get("is_correct"):
                correct_count += 1

            mapped_cid = opt.get("maps_to_concept_id")
            if mapped_cid and mapped_cid not in valid_concept_ids:
                errors.append(f"Question '{qid}' option '{okey}' maps to non-existent concept '{mapped_cid}'.")

        if correct_count != 1:
            errors.append(f"Question '{qid}' must have exactly 1 correct option; found {correct_count}.")

        # Hints validation
        hints = q.get("hints", [])
        hint_levels = [h.get("hint_level") for h in hints]
        if set(hint_levels) - {1, 2}:
            errors.append(f"Question '{qid}' hints must only be level 1 or 2; found {hint_levels}.")

        # Inventory categorization
        is_diag = bool(q.get("use_for_diagnosis"))
        is_retest = bool(q.get("use_for_retest"))
        review_status = q.get("review_status", "draft")

        if primary_cid in concept_question_counts:
            concept_question_counts[primary_cid]["total"] += 1
            if review_status == "reviewed":
                concept_question_counts[primary_cid]["reviewed"] += 1
            else:
                concept_question_counts[primary_cid]["draft"] += 1

            if is_diag:
                concept_question_counts[primary_cid]["diagnostic"] += 1
                concept_diagnostic_families[primary_cid].add(family)
                concept_diagnostic_variants[primary_cid].add(variant_group)
            if is_retest:
                concept_question_counts[primary_cid]["retest"] += 1
                concept_retest_families[primary_cid].add(family)
                concept_retest_variants[primary_cid].add(variant_group)

    # Validate inventory caps & variant disjointness per concept
    for cid in valid_concept_ids:
        counts = concept_question_counts[cid]
        if counts["total"] < 4:
            errors.append(f"Concept '{cid}' has only {counts['total']} questions (minimum 4 required).")
        if counts["retest"] < 1:
            errors.append(f"Concept '{cid}' has 0 retest questions (at least 1 required).")

        # Retest items must differ in family and variant group from diagnostic items they replace
        overlap_variants = concept_diagnostic_variants[cid].intersection(concept_retest_variants[cid])
        if overlap_variants:
            errors.append(f"Concept '{cid}' retest items share variant_group with diagnostic items: {overlap_variants}")

    # --- 3. Validate Resources ---
    valid_depths = {"quick_revision", "standard", "deep_learning"}
    concept_resources: Dict[str, Set[str]] = {cid: set() for cid in valid_concept_ids}

    for idx, r in enumerate(resources_raw):
        cid = r.get("concept_id")
        depth = r.get("depth")
        if cid not in valid_concept_ids:
            errors.append(f"Resource at index {idx} references non-existent concept '{cid}'.")
            continue
        if depth not in valid_depths:
            errors.append(f"Resource at index {idx} has invalid depth '{depth}'. Expected {valid_depths}.")
            continue
        if depth in concept_resources[cid]:
            errors.append(f"Duplicate resource depth '{depth}' for concept '{cid}'.")
        concept_resources[cid].add(depth)

        if not r.get("title") or not r.get("summary") or not r.get("content"):
            errors.append(f"Resource for concept '{cid}' depth '{depth}' has incomplete content.")

    for cid in valid_concept_ids:
        concept_obj = concept_map[cid]
        if not concept_obj.get("resource_unavailable") and len(concept_resources[cid]) < 3:
            missing_depths = valid_depths - concept_resources[cid]
            errors.append(f"Concept '{cid}' is missing resources for depths: {missing_depths}")

    if errors:
        error_summary = f"Curriculum content validation failed with {len(errors)} error(s): " + "; ".join(errors)
        raise SeedValidationError(
            error_summary,
            details={"errors": errors},
        )


    summary = {
        "concepts_count": len(concept_map),
        "edges_count": len(edges_list),
        "questions_count": len(questions_raw),
        "resources_count": len(resources_raw),
        "per_concept_breakdown": concept_question_counts,
    }
    return graph_service, summary


def seed_curriculum(db: Session, data_dir: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
    """Execute repeatable, transactional seed process into the database.

    Idempotently inserts or updates records without dropping existing data.
    """
    if not data_dir:
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

    concepts_path = os.path.join(data_dir, "concepts.json")
    questions_path = os.path.join(data_dir, "questions.json")
    resources_path = os.path.join(data_dir, "resources.json")

    concepts_raw = load_json_file(concepts_path)
    questions_raw = load_json_file(questions_path)
    resources_raw = load_json_file(resources_path)

    # 1. Run strict validation before modifying any database state
    graph_service, summary = validate_curriculum_data(concepts_raw, questions_raw, resources_raw)

    if dry_run:
        return summary

    try:
        # --- 2. Seed Concepts & Edges ---
        for c_data in concepts_raw:
            concept = db.query(Concept).filter(Concept.id == c_data["id"]).one_or_none()
            if not concept:
                concept = Concept(id=c_data["id"])
                db.add(concept)
            concept.name = c_data["name"]
            concept.description = c_data["description"]
            concept.learning_objective = c_data["learning_objective"]
            concept.branch = c_data["branch"]
            concept.resource_unavailable = c_data.get("resource_unavailable", False)

        db.flush()

        # Seed prerequisite edges
        for c_data in concepts_raw:
            dep_id = c_data["id"]
            for prereq_id in c_data.get("prerequisites", []):
                edge = db.query(PrerequisiteEdge).filter(
                    PrerequisiteEdge.prerequisite_id == prereq_id,
                    PrerequisiteEdge.dependent_id == dep_id,
                ).one_or_none()
                if not edge:
                    edge = PrerequisiteEdge(prerequisite_id=prereq_id, dependent_id=dep_id)
                    db.add(edge)

        db.flush()

        # --- 3. Seed Questions, Options, Hints ---
        for q_data in questions_raw:
            qid = q_data["id"]
            q = db.query(Question).filter(Question.id == qid).one_or_none()
            if not q:
                q = Question(id=qid)
                db.add(q)

            q.primary_concept_id = q_data["primary_concept_id"]
            q.learning_objective_id = q_data["learning_objective_id"]
            q.question_family = q_data["question_family"]
            q.difficulty = q_data["difficulty"]
            q.expected_time_s = q_data["expected_time_s"]
            q.prompt = q_data["prompt"]
            q.explanation = q_data["explanation"]
            q.review_status = q_data.get("review_status", "reviewed")
            q.use_for_diagnosis = q_data.get("use_for_diagnosis", True)
            q.use_for_retest = q_data.get("use_for_retest", False)
            q.variant_group = q_data["variant_group"]

            db.flush()

            # Options: update or insert
            existing_options = {opt.option_key: opt for opt in q.options}
            for opt_data in q_data.get("options", []):
                okey = opt_data["option_key"]
                opt = existing_options.get(okey)
                if not opt:
                    opt = QuestionOption(question_id=qid, option_key=okey)
                    db.add(opt)
                opt.text = opt_data["text"]
                opt.is_correct = opt_data["is_correct"]
                opt.maps_to_concept_id = opt_data.get("maps_to_concept_id")
                opt.misconception_code = opt_data.get("misconception_code")
                opt.misconception_text = opt_data.get("misconception_text")

            # Hints: update or insert
            existing_hints = {h.hint_level: h for h in q.hints}
            for h_data in q_data.get("hints", []):
                hlevel = h_data["hint_level"]
                hint = existing_hints.get(hlevel)
                if not hint:
                    hint = QuestionHint(question_id=qid, hint_level=hlevel)
                    db.add(hint)
                hint.content = h_data["content"]

        db.flush()

        # --- 4. Seed Resources ---
        for r_data in resources_raw:
            cid = r_data["concept_id"]
            depth = r_data["depth"]
            res = db.query(Resource).filter(
                Resource.concept_id == cid,
                Resource.depth == depth,
            ).one_or_none()
            if not res:
                res = Resource(concept_id=cid, depth=depth)
                db.add(res)
            res.title = r_data["title"]
            res.summary = r_data["summary"]
            res.content = r_data["content"]

        db.commit()

        # --- 5. Verify graph from database ---
        db_graph = GraphService(
            concept_ids=[c.id for c in db.query(Concept.id).all()],
            edges=[(e.prerequisite_id, e.dependent_id) for e in db.query(PrerequisiteEdge).all()],
            validate_expected=True,
        )
        summary["topological_order"] = db_graph.get_topological_order()
        summary["importance_scores"] = {
            cid: db_graph.get_importance(cid) for cid in db_graph.get_topological_order()
        }

        return summary

    except Exception:
        db.rollback()
        raise


def main() -> None:
    """CLI entrypoint for curriculum seed command."""
    parser = argparse.ArgumentParser(description="Seed MindMesh curriculum data into database.")
    parser.add_argument("--data-dir", type=str, default=None, help="Directory containing curriculum JSON files")
    parser.add_argument("--dry-run", action="store_true", help="Validate curriculum without writing to database")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        print("[MindMesh] Starting curriculum validation and seeding pipeline...")
        summary = seed_curriculum(db, data_dir=args.data_dir, dry_run=args.dry_run)
        print("[MindMesh] Curriculum seed completed successfully!")
        print(f"  - Concepts: {summary['concepts_count']}")
        print(f"  - Edges: {summary['edges_count']}")
        print(f"  - Questions: {summary['questions_count']}")
        print(f"  - Resources: {summary['resources_count']}")
        if "topological_order" in summary:
            print(f"  - Topological Order: {' -> '.join(summary['topological_order'])}")
            print("  - Concept Importance Scores:")
            for cid, score in summary["importance_scores"].items():
                print(f"      {cid}: {score:.4f}")
    except SeedValidationError as exc:
        print(f"\n[MindMesh ERROR] Seed validation failed: {exc.message}", file=sys.stderr)
        if exc.details and "errors" in exc.details:
            for err in exc.details["errors"]:
                print(f"  - {err}", file=sys.stderr)
        sys.exit(1)
    except GraphValidationError as exc:
        print(f"\n[MindMesh ERROR] Graph validation failed: {exc.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"\n[MindMesh ERROR] Unexpected error during seeding: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
