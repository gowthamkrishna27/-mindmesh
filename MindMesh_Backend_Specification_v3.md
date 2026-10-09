# MindMesh Backend Specification

## Implementation-ready MVP: Adaptive Learning Dependency Graph

**Version:** 3.0 (expanded from v1.2)
**Scope:** DBMS diagnostic assessment and adaptive learning, plus educator access to class/section analytics and individual student drill-down restricted to administrator-assigned classes and sections.
**Primary goal:** Explainable, reproducible diagnoses that separate three situations (a misunderstood concept, hesitation between options, a weak prerequisite), choose every next question by learning need, and never claim certainty when evidence is insufficient.

---

## 0. Product narrative

A student gets a question wrong. We know the answer is incorrect, but a final score cannot say why: did they misunderstand the concept, hesitate between options, or struggle with a prerequisite?

MindMesh therefore captures more than the final answer. Option changes, time spent, correctness, and attempt history are signals about how the student approached the question. Together they let us estimate understanding of each concept and say what we observed.

Those estimates are combined with a **dependency graph** that links each concept to its prerequisites. The system finds where the student is struggling and decides what to learn or practise next.

**Worked example (DBMS graph).** A student misses a SQL Joins (D09) question. MindMesh checks their performance on its prerequisite, SQL Basics (D08).

- If SQL Basics is weak, the student is guided back to SQL Basics first. Joins is deferred.
- Once SQL Basics is *ready*, the student moves forward to Joins.
- If SQL Basics is fine, the difficulty is at Joins itself, and the guidance depends on the likely cause (misconception, hesitation, rushed answer).

Every next question is chosen by the student's learning needs, not by a fixed sequence.

---

## 0.1 Changes from v1.1

All v1.1 fixes remain in force. v1.2 adds the signal-aware "why" and prerequisite-first behaviour, and fixes errors found while re-checking v1.1's arithmetic and cross-references.

| # | Issue in v1.1 | Resolution in v1.2 |
|---|---|---|
| 1 | Option changes and time were stored but barely used; the *reason* for a wrong answer was never produced. | 7.1-7.2: option changes and slow answers join the bounded weight adjustments. 7.6: per-answer reason tags. 9.3: diagnosis states a `likely_cause`. |
| 2 | "Attempt history" was undefined. | 7.7: evidence epochs, per-question `attempt_number`, trend and persistence flags. |
| 3 | "Back to basics, then forward" was only implied by retest order. | 9.5: next-step policy with an explicit `ready` test. 8.1: prerequisite probe. 8.4: need-based retest/practice selection. Graph nodes carry `unlocked`. |
| 4 | **Arithmetic error in 7.5 and 5.4.** One fresh correct answer after three wrong gives 2/(2+4) = **0.333** (not 0.444), which is `suspected_gap`, not `uncertain`. Two fresh correct give 0.429; mastery would need nine. So 5 questions per concept could never verify mastery. | 7.5: **evidence epochs.** The first retest answer on a concept opens a new epoch; status uses the current epoch; history is kept. Completing learning alone still changes nothing. 5.4 updated. |
| 5 | 7.4 rules 2-3 said `mastery_estimate` while the preamble said `direct_estimate`; rule 4(a) and "failed concept" did not name an estimate. | Every rule names its estimate. |
| 6 | 8.1 said the highest-importance concept of the Foundation branch is D02, but D01 scores higher (7/7 vs 6/7). | Rule is "highest-importance **non-root** concept per branch"; the fourth baseline question picks D01. |
| 7 | 5.3 required exactly one retest item per concept, 5.4 recommended two. | 1-2 retest items (2 recommended). New setting `MIN_RETEST_ITEMS_PER_CONCEPT`. |
| 8 | No retest outcome for a verified recovery. | 7.5 outcomes: `recovered`, `improving`, `no_change`, `declined`, `not_verified`, plus a `verification_limited` flag. |
| 9 | Slow and idle time unspecified. | `expected_time_s` per question, slow rule, idle cap (7.2). |
| 10 | Resource depth was always a manual choice. | 10: deterministic suggested depth (student may override). |

---

## 1. Product boundary

### 1.1 The pain points

1. **Students do not know why they got a question wrong.** Post-test feedback names the concept, the likely cause (misconception, hesitation, rushed answer, weak prerequisite) and the evidence behind it.
2. **Students practise a hard topic when the blocker may be a prerequisite.** The dependency graph plus explicit evidence rules identify likely root gaps, send the student back to basics, and move them forward once ready.
3. **A score does not explain the learning process or choose what comes next.** Clickable graph with status, evidence, and next action; every next question chosen by need.

### 1.2 In scope

- One focused DBMS graph of 8 concepts.
- Reviewed bank of at least 4 distinct questions per concept (32 minimum); 5 recommended (5.4).
- Diagnostic of at most 12 questions, adaptive, no repeats within a session.
- Event history, final answers, confidence tap, server-measured time, option changes, hints.
- Explainable mastery estimates and gap states; reason tags; root-gap ranking.
- Post-test feedback; four-state clickable map with readiness and unlocked concepts.
- Progressive hints, curated resources, optional AI-labelled explanations.
- Need-based retest from held-out items with prerequisite-first gating.
- Full deterministic behavior with the LLM disabled.
- Logic, API, edge-case, and simulated-student tests.

### 1.3 Out of scope

Multi-subject support, authoring tools, teacher analytics, LMS features, general chatbot/tutor, runtime-generated questions, AI-controlled diagnosis, mobile apps, ML recommenders, and any claim of "99%" accuracy. Auth and consent are minimal (11.0).

---

## 2. Non-negotiable principles

1. **Deterministic diagnosis.** Rules engine, never the LLM, decides mastery, status, reasons, root gaps, readiness, path order, and question selection.
2. **Traceability.** Every diagnosis cites response IDs and graph edges.
3. **No false certainty.** One answer never confirms a gap or mastery. Causes are reported as "likely", with the evidence listed and what could not be determined.
4. **Correctness is primary.** Time, confidence, option changes, and attempt history adjust an answer's weight within a bounded range and explain the *why*; none can decide correctness or confirm anything alone.
5. **One final response = one answer event.** Option changes, timing, hints, and retries are signals attached to that event. They change its weight and its explanation, never the number of events.
6. **Fresh retest.** Different question, same learning objective, different scenario or reasoning operation, not a paraphrase.
7. **LLM optional.**
8. **Honest limitation.** Report insufficient evidence rather than force a result. Missing events never penalise a student.
9. **Simple code.** Plain functions, explicit schemas.
10. **Prerequisites first.** A concept is never practised ahead of a weak, supported prerequisite; progress forward only when prerequisites are `ready`.

---

## 3. Stack

| Layer | Technology |
|---|---|
| API | Python + FastAPI, Uvicorn |
| Validation | Pydantic v2 |
| ORM / DB / migrations | SQLAlchemy 2.x, PostgreSQL, Alembic |
| Graph | NetworkX (DAG validation, ancestors, descendants, topological order) |
| Tests | pytest + httpx |
| Optional LLM | Provider adapter behind an interface |

No NumPy, pandas, scikit-learn, vector DB, or RAG. Pin dependency versions. Secrets only in environment variables.

```text
backend/
  app/
    main.py
    core/ (config.py, errors.py, settings_rules.py)   # all thresholds in settings_rules.py
    api/routes/ (sessions.py, diagnosis.py, graph.py, learning.py)
    schemas/ models/ repositories/
    services/ (graph, question_selector, signals, evidence, mastery, reasons, diagnosis,
               feedback, hint, learning_path, retest, llm/{base,provider})
    data/ (concepts.json, questions.json, resources.json)
    db/ (base.py, session.py, seed.py, migrations/)
  tests/ (unit/, api/, integration/, simulations/)
  pyproject.toml  .env.example  README.md
```

Route handlers validate and delegate to services; they contain no graph or mastery logic.

---

## 4. Focused DBMS graph

| ID | Concept | Prerequisites |
|---|---|---|
| D01 | DBMS Basics | none |
| D02 | Relational Model | D01 |
| D03 | Keys | D02 |
| D04 | Integrity Constraints | D02, D03 |
| D08 | SQL Basics | D02 |
| D09 | SQL Joins | D08 *(demo simplification: the full curriculum also needs D07 Relational Algebra, which is excluded)* |
| D12 | Functional Dependencies | D03 |
| D13 | Normalization (1NF-3NF) | D12, D03 |

Edge direction is `prerequisite -> dependent`. Document the D09 simplification in the README and never present this as a complete DBMS curriculum.

**Branches** (used for baseline coverage): *Foundation* {D01, D02}, *Design* {D03, D04, D12, D13}, *SQL* {D08, D09}.

**Importance** (descendant count / 7): D01 7/7, D02 6/7, D03 3/7, D08 1/7, D12 1/7, D04 0, D09 0, D13 0.

**Startup validation (fail fast with an actionable error, never silently drop):** edge endpoints exist; no self-edge; no duplicate edge; no cycle; every concept has name, description, learning objective, and a resource or explicit `resource_unavailable` state; every concept has at least 4 reviewed diagnostic questions and at least `MIN_RETEST_ITEMS_PER_CONCEPT` retest candidates; all question and distractor concept IDs exist; every question has a positive `expected_time_s` (or a difficulty default).

---

## 5. Question bank

### 5.1 Content requirements

At least 4 reviewed questions per concept (32 minimum). Each has: `id`, `primary_concept_id`, `learning_objective_id`, `question_family`, `difficulty` (1-5), `expected_time_s` (defaults by difficulty, see 7.2), `prompt`, exactly four options with exactly one correct, `explanation`, distractor misconception mapping where appropriate, `review_status = reviewed`, `use_for_diagnosis`, `use_for_retest`, `variant_group`.

Families are cognitive operations: recognition, interpretation, application, error analysis. Aim for as many distinct families per concept as the bank size allows. **The held-out retest items must differ in family and `variant_group` from the diagnostic items they replace**; paraphrases do not count as distinct.

### 5.2 Distractor mapping

A distractor may store `maps_to_concept_id`, `misconception_code`, `misconception_text`. Selecting it is still one response event (see 7.2) and produces a `misconception` reason tag (7.6).

### 5.3 Diagnostic vs retest vs practice inventory

- Diagnostic selector uses only reviewed diagnostic questions.
- **Per-concept diagnostic cap: 3 questions** (so retest items stay held out). **1-2 items per concept** (2 recommended) are flagged `use_for_retest = true` and excluded from diagnosis while any other eligible item exists.
- If no fresh item exists, never reuse a seen item as "fresh"; the outcome is `not_verified` with `verification_limited = true` (7.5).
- Retest is a separate session that uses held-out items.
- Practice serves reviewed items of the opened concept, excluding retest-reserved items. A previously answered item may be re-served when no unseen one remains; that response gets `attempt_number > 1` and adds no evidence (7.7).

### 5.4 Decision for you: bank size

With 4 per concept: diagnosis can use 3, retest has exactly 1. Under v1.2's epoch rule (7.5), one fresh correct answer gives 0.667 (`uncertain`, `ready`, outcome `improving`, `verification_limited = true`); mastery is not verifiable. **Recommended: 5 per concept (40 total)**: 3 diagnostic + 2 retest, so two fresh correct answers give 0.750 and `mastered` can be verified. 4 remains an acceptable MVP minimum if the limitation is shown honestly. Read the targets from settings (`MIN_QUESTIONS_PER_CONCEPT`, `MIN_RETEST_ITEMS_PER_CONCEPT`).

*(v1.1 claimed 5 per concept already worked without epochs. It did not: see 0.1 item 4.)*

---

## 6. Session workflow

### 6.1 Diagnostic flow

1. Student consents before their first stored assessment.
2. Backend creates a diagnostic session.
3. Backend issues one question at a time with confidence options `not_sure | fairly_sure | sure`.
4. Frontend sends interaction events (selections, option changes, hint attempts); backend records the final answer.
5. No correctness or explanation is shown during diagnosis; neutral progress only.
6. After each final answer, signals, reason tags, evidence, and mastery update deterministically.
7. Next question: baseline coverage first, then prerequisite probe and ranked selection (8.1).
8. Stop when the student submits, 12 answers are recorded, or no eligible question remains.
9. Compute diagnosis, likely causes, root gaps, readiness, rationale, ordered path.
10. Return post-test feedback and graph data.

### 6.2 Learning flow

1. Student opens a concept from the map or path.
2. Curated resources by depth: `quick_revision`, `standard`, `deep_learning`; a suggested default depth is preselected (10).
3. Optional hints during practice (level 1, level 2, level 3 = reveal explanation); usage recorded.
4. Immediate correctness feedback during practice. Re-served questions are recorded as repeat attempts without new evidence.
5. Optional AI explanation, labelled AI-assisted; never affects diagnosis.
6. On completion, create or enable a retest session with held-out questions if available. Completion changes no estimate, status, or epoch.
7. Retest follows 8.4: prerequisites first; move forward only when a concept is `ready`.
8. The first retest answer on a concept opens a new evidence epoch for it (7.5). Recompute and store a **new** snapshot; keep the earlier one.

### 6.3 Phase-dependent feedback

| Phase | Student sees |
|---|---|
| Diagnostic question | Question, options, confidence tap, progress. No correctness or explanation. |
| Diagnostic finished | Correct answer, explanation, concept, evidence used, likely cause, diagnosis, uncertainty. |
| Practice | Hints and immediate feedback. |
| Retest submitted | Feedback plus updated diagnosis, readiness, next step, and map. |

---

## 7. Evidence and mastery

### 7.1 Event history vs answer evidence

Record: question displayed, first interaction, option selections and changes, hint requests, final answer, confidence, duration, timestamps. **Only the final submitted answer is a correctness event.**

**Signals the server derives for each answered question** (from its own stored events and clock; the client's numbers are never trusted):

| Signal | Definition |
|---|---|
| `response_time_ms` | `answered_at - issued_at` (server clock). `client_response_time_ms` is stored for audit only. |
| `time_class` | `fast`: under 3 s. `slow`: over 2 x `expected_time_s` and not over the idle cap. `away`: over the idle cap (5 min), treated as inactivity, no adjustment. Otherwise `normal`. |
| `option_changes` | Count of stored `option_changed` events for this issue where `from_option_id` is not null, capped at 10. |
| `first_selected_option_id` | `to_option_id` of the first selection event. |
| `hesitated` | `option_changes >= 2`. |
| `switched_from_correct` | First selected option was the correct one and the final answer is incorrect. |
| `signals_incomplete` | No selection events stored for this issue (dropped network, old client). All option-change signals are then treated as absent: **no adjustment, no penalty.** |

Client-sent events can be spoofed or lost. That is acceptable because signals only adjust weights within the clamp below and can never confirm a status alone.

### 7.2 Estimate (heuristic, not a calibrated probability)

Start `weighted_correct = 1.0`, `weighted_incorrect = 1.0` (estimate 0.5). Per eligible final answer, compute weight `w`:

1. **Base:** 1.0. Correct and `not_sure`: 0.6. Incorrect and `sure`: 1.2.
2. **Multipliers** (all that apply):

| Signal | Correct answer | Incorrect answer | Why |
|---|---|---|---|
| `time_class = fast` | x 0.7 | x 0.7 | Likely a guess or a rush: weaker evidence either way. |
| `hesitated` | x 0.85 | x 0.90 | Correct but shaky; or wrong while torn between options, a less firm misunderstanding. |
| `time_class = slow` | x 0.85 | x 1.0 | Correct but effortful. A slow wrong answer is a real attempt, so it keeps full weight. |
| `assisted` | x 0.5 | x 0.5 | Hints were used. |

3. **Clamp** to `[0.25, 1.2]`.

Add `w` to the matching total. `mastery_estimate = weighted_correct / (weighted_correct + weighted_incorrect)`.

Signals never change whether an answer counts as correct or incorrect in `n_direct_*`.

**Mapped misconception:** an incorrect response whose selected distractor maps to another concept updates the primary concept with `w` (`primary_direct`, negative) and the mapped concept with `0.5 * w` (`mapped_misconception`, negative). Both rows reference the same response ID. The mapped concept counts the question in `n_direct_questions` and `n_direct_incorrect`, but see the confirmation rule in 7.4.

**Restrictions:** assisted answers never count toward confirmation; diagnostic questions show no hints; confidence, time, option changes, attempts never confirm anything alone. Responses with `attempt_number > 1` create no evidence rows.

**Settings (`settings_rules.py`):** `FAST_MS=3000`, `SLOW_MULTIPLIER=2.0`, `IDLE_CAP_MS=300000`, `HESITATION_MIN_CHANGES=2`, `W_HESITATED_CORRECT=0.85`, `W_HESITATED_INCORRECT=0.90`, `W_SLOW_CORRECT=0.85`, `EXPECTED_TIME_BY_DIFFICULTY={1:20, 2:30, 3:45, 4:60, 5:90}` (seconds, overridable per question), `READY_MIN_ESTIMATE=0.60`, `TREND_DELTA=0.10`, plus all earlier thresholds.

### 7.3 Indirect prerequisite evidence

For a response on concept X, each **direct** prerequisite P of X gets:

- incorrect answer: negative weight `0.3 * w` added to `weighted_incorrect`
- correct answer: positive weight `0.15 * w` added to `weighted_correct`

Increment `n_indirect` only. Never touch `n_direct_*`. Do not propagate beyond direct prerequisites. Store `source_concept_id` and edge. Indirect evidence lands in P's **current epoch** (7.5). It can raise suspicion and affect ranking; it cannot confirm a gap, mastery, or readiness (all require direct counts).

### 7.4 Status rules (evaluated in this order, on the concept's current epoch)

**Two estimates are stored.** `mastery_estimate` includes indirect evidence; it is what the map displays and what selection and ranking use. `direct_estimate` uses direct and mapped evidence only (same 1.0/1.0 prior). **confirmed_gap, mastered, suspected_gap (a), and readiness use `direct_estimate`**, so indirect evidence can never tip a concept across those lines (two `not_sure` correct answers = 0.6875; one indirect positive would lift the blended estimate to 0.7015 and wrongly master it). Suspected-gap rule (b) is the only status rule using the blended estimate.

1. **unassessed**: `n_direct_questions == 0` and `n_indirect == 0`.
2. **confirmed_gap**: at least 3 distinct direct questions, all answered incorrectly, unassisted; at least 2 of them primary-concept questions (third may be mapped); `direct_estimate < 0.30`.
3. **mastered**: at least 2 distinct direct questions, at least 2 direct correct, `direct_estimate > 0.70`.
4. **suspected_gap**: not confirmed, and either (a) `n_direct_incorrect >= 1` and `direct_estimate < 0.40`, or (b) `n_direct_questions == 0`, `n_indirect > 0`, and `mastery_estimate < 0.40`.
5. **uncertain**: everything else with some evidence (mixed answers, middle estimate, thin evidence, or out of eligible questions).

**Readiness** (a flag next to status, not a new map state): a concept is `ready` if its status is `mastered`, **or** `n_direct_incorrect == 0` and at least one direct unassisted answer is correct and `direct_estimate >= 0.60`. Readiness answers one question: *is it safe to move on to concepts that depend on this one?*

**Hand-checked examples** (w = 1 unless stated; current epoch):

| Direct answers | Estimate | Status |
|---|---|---|
| wrong | 0.333 | suspected_gap |
| wrong, wrong | 0.250 | suspected_gap |
| wrong x3 | 0.200 | confirmed_gap |
| wrong x3, all fast (0.7) | 0.244 | confirmed_gap |
| wrong x3, all hesitated (0.9) | 0.213 | confirmed_gap |
| wrong, hesitated (0.9) | 0.345 | suspected_gap |
| right | 0.667 | uncertain (ready) |
| right, hesitated (0.85) | 0.649 | uncertain (ready) |
| right, right | 0.750 | mastered |
| right, right, both hesitated (0.85) | 0.730 | mastered |
| right, right, both `not_sure` (0.6) | 0.6875 | uncertain (not mastered; ready) |
| right, right, both `not_sure` and hesitated (0.51) | 0.669 | uncertain (not mastered; ready) |
| right, wrong | 0.500 | uncertain (not ready) |
| wrong, wrong, right | 0.400 | uncertain (not ready) |
| right, right, wrong | 0.600 | uncertain (not ready) |

Speed alone cannot confirm: three fast wrong answers still require three distinct wrong questions, and a gap confirmed this way is flagged "fast responses" in the rationale.

**Visual states:** Mastered <- `mastered`; Needs attention <- `confirmed_gap` / `suspected_gap` (distinction shown in click panel); Uncertain <- `uncertain`; Unassessed <- `unassessed`. Label the number "estimated mastery", never "confidence" or "probability".

### 7.5 Evidence epochs, retest evidence, honest outcomes

**Why epochs.** With one running total and no reset, recovery is arithmetically unreachable: after three wrong answers (0.200), one fresh correct gives 0.333, two give 0.429, and mastery (> 0.70) needs nine. A student who has learned the material would look permanently weak, and "move forward once ready" could never happen.

**Rule.** Each concept has an evidence epoch, starting at 0. **The first answer in a retest session whose primary concept is C opens a new epoch for C** (increment before applying that answer's evidence). Status, estimates, counts, and readiness for C are computed from the **current epoch only**, starting again from the 1.0/1.0 prior. Earlier epochs are never deleted: they are the attempt history (7.7) and the "before" values in the report.

- Epochs open only on retest answers, never on completing a learning item, so completion alone still changes nothing, and until the retest the map shows the last assessed state.
- Only the retest's *primary* concept opens an epoch; mapped and indirect rows land in the affected concept's current epoch.
- Replay (12) re-derives epochs by processing responses in order.

Retest answers use the same weights (assisted still halves).

**Examples** (previous epoch ended `confirmed_gap`, estimate 0.200):

| Fresh answers (new epoch) | Estimate | Status | Ready | Outcome |
|---|---|---|---|---|
| none | prior epoch retained | confirmed_gap | no | `not_verified` |
| right | 0.667 | uncertain | yes | `improving`, `verification_limited` |
| right (`not_sure`, 0.6) | 0.615 | uncertain | yes | `improving`, `verification_limited` |
| right, right | 0.750 | mastered | yes | `recovered` |
| right, wrong | 0.500 | uncertain | no | `improving` |
| wrong | 0.333 | suspected_gap | no | `no_change`, `verification_limited` |
| wrong, wrong | 0.250 | suspected_gap | no | `no_change` |

**Outcome rules** (per concept, in the report, not as new map states). Let rank be confirmed_gap 3, suspected_gap 2, uncertain 1, mastered 0, comparing the previous epoch's final status with the current one:

1. No fresh answers: `not_verified`.
2. All fresh answers incorrect: `no_change` if the previous rank was at least 2, otherwise `declined`.
3. At least one fresh correct: current status `mastered` gives `recovered`; lower rank than before gives `improving`; equal rank gives `no_change`; higher rank gives `declined`.

`verification_limited = true` when the concept has fewer than 2 fresh unassisted direct answers (with a single held-out item mastery cannot be verified). Completing a learning item never changes mastery.

*Assumption to verify:* thresholds (0.30 / 0.40 / 0.60 / 0.70, 3 questions) are conservative starting values, not validated educational thresholds. Tune using real pilot data.

### 7.6 Why was it wrong? Reason tags and likely cause

**Per-answer tags** (deterministic, from 7.1 signals; stored on the response):

| Tag | Applies to | Condition |
|---|---|---|
| `misconception` | incorrect | Selected distractor has a mapping (stores `misconception_code`, `maps_to_concept_id`). |
| `confident_error` | incorrect | Confidence `sure` and no distractor mapping. |
| `hesitation` | incorrect | `hesitated` or `switched_from_correct`. |
| `rushed` | incorrect | `time_class = fast`. |
| `slow` | incorrect | `time_class = slow`. |
| `shaky_correct` | correct | `not_sure`, or `hesitated`, or `time_class = slow`. |

Several tags can apply. Tags are descriptions of observed behaviour, not claims about the student.

**Concept-level likely cause** (for each concept with status `confirmed_gap` or `suspected_gap`; first match wins):

1. `prerequisite_gap`: an ancestor of the concept has status `confirmed_gap` or `suspected_gap` (the chosen root, 9.1). Never based on downstream failure alone.
2. `misconception`: at least one incorrect direct answer in the current epoch carries a `misconception` tag whose mapped concept is this concept.
3. `confident_error`, 4. `hesitation`, 5. `rushed`: the tag appears on more than half of the concept's incorrect direct answers in the current epoch.
6. `unclear`: none of the above. The system says it cannot tell why.

Every other qualifying cause is listed as `also_observed`. A concept that is only `uncertain` gets no likely cause; it gets a `limitation_reason` (thin evidence, `shaky_correct` answers, mixed answers). The cause drives the recommended action (9.5); `also_observed` is context.

### 7.7 Attempt history

Attempt history is everything the student has done on a concept, kept replayable:

- **Cumulative evidence:** every final answer from every session is stored; estimates are derived from the current epoch (7.5) and earlier epochs stay available.
- **Epoch history** per concept: `[{epoch_index, n_direct_answers, final_direct_estimate, final_status, opened_by_session_id}]`.
- **Question-level:** `attempt_number` = how many times this student has answered this question across sessions. Repeats (`attempt_number > 1`) are recorded, shown in feedback, and add **no** evidence (memory contaminates them).
- **Derived flags:** `trend` from the last two epochs' final direct estimates: `improving` if up by `TREND_DELTA` (0.10) or more, `declining` if down by that much, else `flat`, and `none` with one epoch. `persistent_gap` is true when a previous epoch ended in `confirmed_gap` or `suspected_gap` and the current epoch (with at least one answer) is also in a gap status.

These flags feed the rationale text, the suggested resource depth (10), and the report. They do not change estimates.

---

## 8. Adaptive selection

### 8.1 Phases (12 answers max)

- **Baseline** (up to 4): cover distinct branches first. Order: highest-importance **non-root** concept in each of the 3 branches (D02, D03, D08 for this graph; D01 is the graph root and is informed by indirect evidence from D02), then the highest-importance unsampled concept overall (D01).
- **Targeted** (up to 6):
  1. **Prerequisite probe.** Find the most recently failed concept T (by `answered_at`) that has a direct prerequisite P with no direct question yet this session and at least one eligible question. If found, issue a question on P (if several P, larger importance first, then ID). At most one probe per (T, P) pair.
  2. Otherwise ranked selection (8.3).
- **Verification** (up to 2): a different question on a suspected or uncertain concept, only if it adds independent evidence.
- Unused budget carries forward; fewer than 12 is allowed when no question adds evidence.

### 8.2 Eligibility

Exclude a question if: already issued in this session; not reviewed or not diagnosis-approved; it is a held-out retest item for its concept and another eligible item exists; the concept already has 3 diagnostic questions in this session; the session has 12 answers.

### 8.3 Ranking

Per candidate concept, normalized to `[0,1]`:

- `U = 1 - abs(2*mastery_estimate - 1)`
- `I = descendant_count(concept) / (n_concepts - 1)`
- `S = min(1, (weighted_incorrect - 1) / 3) + 0.25 * [concept is a direct prerequisite of a failed concept]`, capped at 1
- `C = 1` if the concept's branch has no question yet this session, else `0`

`rank_score = 0.40*U + 0.25*I + 0.25*S + 0.10*C`

Tie-breakers: (1) prerequisite of a failed concept; (2) stronger direct evidence of difficulty; (3) concept not yet asked; (4) stable question ID order. Within a chosen concept, prefer an unused question family. Persist candidate scores and the winning reason (including "prerequisite probe") for explainability. The LLM never selects questions.

**Failed concept** (used here and in 9): a concept with `n_direct_incorrect >= 1` and `direct_estimate < 0.5`.

### 8.4 Need-based selection in retest and practice

**Retest.** The target set is the latest snapshot's root gaps and weak targets, deduplicated, in topological order (prerequisites first). Repeatedly:

1. Pick the earliest concept in the target set that is not yet `ready` and has a fresh held-out item (prefer an unused family and `variant_group`).
2. After each answer, recompute readiness.
3. When a concept becomes `ready`, move on to the next target (this is "move forward once ready").
4. If a concept is not `ready` and has no fresh item left, **stop forward progress**: mark all its dependents in the target set `deferred` (not asked this session), finalize, and set the next action to `repeat_prerequisite` for that concept with `deep_learning` as the suggested depth.

**Practice** (single opened concept): serve an unseen non-reserved question if one exists, else a repeat (5.3). Prefer difficulty closest to `target_difficulty = 1 + round(4 * direct_estimate)`; ties by unused family, then ID.

Persist the reason and candidate scores in `selection_log` for both.

---

## 9. Root gaps and next steps

### 9.1 Candidates

For each failed target: take its ancestors; consider `confirmed_gap` ancestors first, then `suspected_gap`; never promote an ancestor on downstream failure alone; include the target itself if still weak (status confirmed/suspected). `uncertain` or `unassessed` ancestors are listed under "needs more evidence", not as root gaps.

### 9.2 Ranking

`blocker_score = (1 - mastery_estimate) * importance`, where importance = share of the other concepts that depend on it, directly or transitively. Tie-breakers: stronger direct evidence; more failed dependents explained; deepest prerequisite (closest to foundation); concept ID. Return all supported roots in order, not every ancestor.

### 9.3 Diagnosis payload

Root-gap concept ID/name; status; estimate (labelled as estimate); readiness; evidence response and question IDs; selected options and correctness; **`likely_cause`, `also_observed`, and a signals summary** (option changes, time classes, confidence); misconception text if mapped; prerequisite path from root to target; one plain-language, template-based explanation; recommended next action; suggested resource depth; trend and `persistent_gap`; limitation reason when evidence is thin.

**Explanation templates** (the LLM may rephrase but cannot add evidence or change status):

| Cause | Template |
|---|---|
| `prerequisite_gap` | "You missed {Q} on {target}. Your answers on {root}, which {target} builds on, also show a gap, so review {root} first." |
| `misconception` | "You chose an option linked to {misconception_text} on {Q}." |
| `confident_error` | "You were sure of your answer on {Q} but it was incorrect, which suggests a misunderstanding of {concept}." |
| `hesitation` | "You changed your answer {n} times on {Q} before choosing an incorrect option, which suggests you were torn between options." |
| `rushed` | "You answered {Q} in {s} seconds, so it may have been a quick guess." |
| `unclear` | "You missed {Q}, but the signals do not show why." |

Example: "Functional Dependencies needs review. You missed Q-D12-B and chose an option linked to confusing dependency direction. Normalization depends on Functional Dependencies. We have not yet collected three distinct incorrect answers, so this is a suspected gap, not a confirmed one."

### 9.4 Learning path

Topological order of selected roots and their weak targets, deduplicated; prerequisites always precede dependents. Items have `kind`: `fix_prerequisite`, `target`, or `advance`. After all weak items are `ready`, the path adds up to 2 `advance` items from the frontier (below), lowest topological position first. A `deferred` flag marks items waiting on an unready prerequisite.

**Frontier / unlocked:** a concept is `unlocked` if it is not `mastered` and all its direct prerequisites are `ready`.

### 9.5 Next-step policy: back to basics, then forward

For each weak concept T (first match wins):

| Condition | Action | Meaning |
|---|---|---|
| A supported root R (ancestor, not T) exists | `fix_prerequisite(R)` | Learn R first; T is deferred. |
| Some direct prerequisite P of T is not `ready` (unassessed, or uncertain and not ready) | `verify_prerequisite(P)` | Ask a check question on P before practising T. If P has no eligible question, say so and continue. |
| All direct prerequisites are `ready`, cause `misconception` | `address_misconception` | Explanation for the `misconception_code`, then targeted practice. |
| ... cause `confident_error` | `review_concept` | Standard resource, then practice. |
| ... cause `hesitation` | `consolidate` | Quick revision plus unassisted practice to build fluency. |
| ... cause `rushed` | `recheck_carefully` | One more question on T, answered without rushing. |
| ... cause `unclear` or evidence thin | `verify` | One more independent question on T. |

Forward movement:

- When R becomes `ready` after its retest, T becomes the next item (`advance_to(T)`) and T is retested.
- If R is not `ready` and has no fresh item left, T stays deferred and R's action becomes `repeat_prerequisite` with `deep_learning` suggested.
- `mastered` or `ready` concepts expose their dependents through `unlocked`; the path's `advance` items come from there.

---

## 10. Resources, hints, optional LLM

- Resources per concept at three depths; curated first; a missing resource returns an explicit placeholder and never fails a map or path request.
- **Suggested depth** (the student may choose any): `deep_learning` if `persistent_gap` or the action is `repeat_prerequisite`; `standard` for `confirmed_gap`, `misconception`, and `confident_error`; `quick_revision` otherwise.
- Hints: level 1 nudge, level 2 conceptual clue (both stored); level 3 reveals explanation and answer. Levels must be requested in order. Hints only in practice sessions; they mark the answer `assisted`.
- LLM: may rephrase curated explanations or the 9.3 templates, or give an aligned example; may not generate diagnostic questions, change correctness, mappings, reason tags, causes, mastery, readiness, graph, roots, or path, and never receives student identifiers. Strict structured output, 3 s timeout, curated fallback on failure, outputs labelled AI-assisted.

---

## 11. API contract (`/api/v1`)

### 11.0 Auth

**Student auth (existing v1.2 behavior):** Minimal bearer-token auth resolves `students/me`. Every student query is scoped to that student; cross-student access returns 403/404. Consent is recorded on the student before the first stored session.

**Educator and administrator auth (v3):** Use separate role-aware identities and authorization dependencies. Do not let a client-supplied role, educator ID, student ID, class ID, or section ID grant access. Every protected request derives the acting identity from a validated bearer token and checks current database state. Return 401 for missing/invalid authentication and 403 or 404 for unauthorized resource access without leaking whether another student's record exists. Do not change student diagnosis rules to implement educator access.

Educator registration creates a `pending` educator account. Pending, suspended, or unapproved educators cannot access student records, diagnoses, analytics, or class lists. Only an administrator can approve/suspend educators and create or remove class/section assignments. Approval alone grants no student-data access: at least one active assignment is required. Removing approval or an assignment takes effect on the next request; do not rely on long-lived role/assignment claims inside tokens. Store secrets only in environment variables and never log credentials or tokens.

### 11.1 `POST /sessions`

`{"kind": "diagnostic"|"retest"|"practice", "consent": true}` returns `{session_id, kind, status, question_limit, answered_count}`. Reject missing/false consent (400). Retest requires an existing completed diagnostic. Practice requires `concept_id`.

### 11.2 `GET /sessions/{id}/next`

**Idempotent:** if an issued question is unanswered, return the same one; otherwise select (8.1 or 8.4) and issue a new one (recording `issued_at`). No `correct_option_id` or explanation in diagnostic or retest sessions. If none remain, complete the session with `completion_reason = question_bank_exhausted` (or `prerequisite_not_ready` when 8.4 stops forward progress) and finalize.

### 11.3 `POST /sessions/{id}/events`

Allowed types: `question_displayed`, `first_interaction`, `option_changed`, `hint_requested`, `submit_intent`. `option_changed` payload: `{from_option_id (null for the first selection), to_option_id}`. Allowlisted payload, size-limited. Events are tied to the currently issued question.

### 11.4 `POST /sessions/{id}/answers`

Request: `question_id`, `selected_option_id`, `confidence`, `client_response_time_ms` (optional, audit only), `assisted` (server verifies against recorded hint events; client value cannot lower it), `event_ids` (audit linking only).
Server: checks active session and issued question, rejects duplicates (409), computes correctness, timing, and all 7.1 signals itself from stored events, derives reason tags, stores response plus evidence rows plus mastery update in one transaction, and returns progress only during diagnosis.

### 11.5 `POST /sessions/{id}/submit`

Finish early; finalize snapshot and path. Also happens automatically at 12 answers or exhaustion. Repeat call returns the existing result.

### 11.6-11.12 Student endpoints

- `GET /students/me/diagnosis`: latest snapshot (including likely causes and next actions).
- `GET /students/me/graph`: nodes (id, name, visual status, estimate, direct count, uncertainty flag, short reason, on-path flag, **`ready`, `unlocked`, `likely_cause`, `trend`**) and edges (prerequisite -> dependent).
- `GET /students/me/concepts/{id}`: description, objectives, visual and backend status, estimate, evidence IDs, **reason tags with response IDs, likely cause, attempt history (epochs, trend, `persistent_gap`)**, reason text, prerequisites/dependents, resources at all depths with the suggested depth, hints/practice actions, next action.
- `GET /students/me/feedback`: only after finalization.
- `POST /students/me/concepts/{id}/hints`: `{question_id, requested_level}`; enforces order.
- `POST /students/me/learning/{id}/complete`: creates or enables a retest session; does not change mastery or open an epoch.
- `GET /students/me/report`: before/after estimates and statuses per epoch, questions used, outcome label and `verification_limited` (7.5), readiness, deferred items, remaining uncertainty.

### 11.13 Errors

`{"error": {"code", "message", "details"}}`. Statuses: 400 invalid payload, 401/403 auth, 404 unknown, 409 invalid state or duplicate, 422 schema, 500 unexpected. No stack traces or secrets.

---

## 12. Database

SQLAlchemy models plus Alembic. Tables (key columns only; keep v1.0 constraints):

`concepts`; `prerequisite_edges` (composite PK, no self-edge check); `questions` (adds `expected_time_s`); `question_options` (unique `(question_id, option_key)`, exactly one correct validated at seed); `question_hints` (level 1 or 2); `resources`; `students`; `educators`; `administrator_accounts`; `educator_class_assignments`; `sessions`; `session_question_issues` (unique `(session_id, question_id)`, stores `issued_at`); `interaction_events`; `responses` (unique `(session_id, question_id)`; adds `client_response_time_ms`, `response_time_ms`, `time_class`, `option_changes`, `first_selected_option_id`, `switched_from_correct`, `signals_incomplete`, `reason_tags`, `attempt_number`); `response_evidence` (unique on `(response_id, concept_id, evidence_type)`; adds `epoch_index`); **`concept_epochs`** (student_id, concept_id, epoch_index, opened_by_response_id, opened_at); `student_concept_mastery` (current epoch: `epoch_index`, `mastery_estimate`, `direct_estimate`, counts, `n_direct_correct_unassisted`, status, `ready`); `diagnosis_snapshots` (immutable; per concept: estimates, status, ready, epoch, likely cause, also-observed, action, suggested depth); `learning_path_items` (adds `kind`, `deferred`).

**Source of truth:** responses plus response_evidence plus concept_epochs. Mastery is derived and must be rebuildable by replay (including epochs and signals); ship a replay service and test.

**Selector audit:** add `selection_log` (session_id, question_id, candidate scores JSON, reason).

---

## 13. Consistency and failure handling

One transaction per answer: validate, derive signals, insert response, insert evidence, open epoch if due, update mastery and status, update session count, commit; roll back everything on any failure. Idempotency by unique constraints (409, or return the stored result). Graph errors fail startup. Missing resource gives placeholder. Missing events give `signals_incomplete` and no adjustment. Exhausted bank finalizes with limitation. LLM failure gives curated fallback. No fresh retest item gives `not_verified` with `verification_limited`. Log request and session IDs only; no personal data or secrets.

---

## 14. Acceptance tests

**Graph:** cycle, dangling ID, self-edge, duplicate edge rejected; topological order valid; ancestor/descendant correct for multi-prerequisite nodes; importance deterministic; `unlocked` correct for multi-prerequisite nodes.

**Question bank:** at least `MIN_QUESTIONS_PER_CONCEPT` reviewed per concept; at least `MIN_RETEST_ITEMS_PER_CONCEPT` retest items per concept; four options, one correct; mapped IDs exist; `expected_time_s` present or defaulted; retest items differ in family and variant group.

**Signals:** server time ignores client time; `fast`, `normal`, `slow`, `away` boundaries; option changes counted from stored events only; first selection excluded from the count; `switched_from_correct`; missing events set `signals_incomplete` with no weight change; spoofed events cannot push weight outside `[0.25, 1.2]`.

**Evidence/mastery:** initial 0.5; replicate every row of the 7.4 example table as a test; one wrong never confirms; two wrong never confirm; three distinct unassisted wrong with direct estimate under 0.30 confirm; mapped-only third answer allowed but two-mapped cannot confirm; repeat question does not raise direct count and creates no evidence; one correct never masters; two correct with `not_sure` weights does not master; hesitated correct weighs 0.85, hesitated wrong 0.90, slow correct 0.85, slow wrong 1.0; low-confidence correct weighs less; sure-wrong modestly more (cap 1.2); under-3 s downweighted but never alone confirms; assisted never counts toward confirmation or readiness; mapped distractor updates mapped concept once; indirect evidence changes `n_indirect` only and cannot confirm, master, or make ready (regression test: two `not_sure` correct answers plus indirect positives stays `uncertain`); replay reproduces state, epochs, and signals.

**Epochs and retest evidence:** first retest answer on C opens epoch 1 for C and no other concept; learning completion opens no epoch and changes nothing; replicate every row of the 7.5 example table (estimate, status, readiness, outcome); second answer in the same retest session does not open another epoch; prior epoch preserved and queryable; mapped/indirect rows from a retest land in the affected concept's current epoch; `trend` and `persistent_gap` correct.

**Reasons:** each tag fires only on its condition; `prerequisite_gap` only when an ancestor has its own gap status (never on downstream failure alone); `misconception` beats `confident_error` beats `hesitation` beats `rushed`; majority rule for tags 3-5; uncertain concepts get a limitation reason, not a cause; `also_observed` lists the rest; templates cite real response IDs.

**Selection:** baseline spans three branches and picks non-root concepts (D02, D03, D08) then D01; prerequisite probe fires after a failure and at most once per (T, P); prerequisites of failed concepts become candidates; scores and ties deterministic; no repeat; at most 12; at most 3 per concept; held-out items reserved; clean end on exhaustion; `GET /next` idempotent. **Retest:** prerequisites first; moves forward only when `ready`; unready prerequisite with no fresh item defers dependents and ends with `prerequisite_not_ready`; practice difficulty follows `target_difficulty`.

**Diagnosis/map:** roots are ancestors of failed targets or the target itself; confirmed outranks suspected; unassessed never shown as gap; uncertain ancestors not listed as roots; next-action table (9.5) applied in order; rationale cites real response IDs and valid edges; diagnosis, path, and map agree; visual-state mapping correct; `ready` and `unlocked` consistent with 7.4 and 9.4.

**Feedback/hints:** no answer leak in diagnostic `/next`; post-test feedback complete; hints in order and answer-free at levels 1-2; hints mark assisted and add no direct diagnostic evidence; LLM failure falls back; LLM cannot alter tags, causes, or state; suggested resource depth follows section 10.

**Retest outcomes:** fresh question ID and family; root then target, deduplicated; single fresh correct after confirmed gap yields `improving` with `verification_limited`, not `mastered`; two fresh correct yield `recovered`; no fresh item yields `not_verified`; new snapshot, original preserved; completion alone changes nothing.

**API/security:** client correctness ignored; unissued question rejected; duplicate submit not double-counted; state errors clear; cross-student access blocked; no secrets in responses; request and response schema validation.

**Simulations (deterministic):** strong student; foundational gap (Keys or FDs); SQL Basics blocker then forward to Joins; careless fast answers; hesitant student (option changes, mostly correct); confident misconceptions; conflicting evidence; question exhaustion; multiple roots; retest improvement; persistent gap after two cycles; LLM unavailable; missing resource; bank shortage. These validate rule behavior only, not real educational effectiveness.

---


---

## 19. v3 educator access and administrator workflow

This section extends v1.2. It does **not** change the deterministic diagnosis, mastery, evidence, selection, retest, or student-facing rules defined above.

### 19.1 Roles

- `student`: can access only their own sessions, diagnosis, graph, feedback, concepts, hints, learning path, and report.
- `educator`: can access class-level analytics and individual student drill-down only for currently assigned class/section combinations.
- `administrator`: can approve/suspend educators and manage educator class/section assignments. Administrator access is not a reason to bypass audit logging or authentication.

Do not implement public administrator registration. A user must never be able to choose `administrator` during registration or promote their own role.

### 19.2 Educator registration and activation

1. An educator submits registration details.
2. The account is created with `status = pending`; it has no access to student data.
3. An authenticated administrator reviews the account and approves or rejects it. Rejection/suspension must not grant access.
4. An administrator assigns one or more class/section combinations to the approved educator.
5. The educator can then access only those assigned scopes.
6. If the educator is suspended, approval is revoked, or an assignment is removed, authorization fails immediately on subsequent requests.

Use a minimal set of registration fields (for example, name, email, and password) and validate them. Do not collect unnecessary personal information. Passwords must be securely hashed with a suitable password-hashing library; never store plaintext passwords. Apply unique constraints to normalized educator email addresses. Registration must not expose whether a password or secret is valid.

**Initial administrator bootstrap:** v1.2 did not define this. For the MVP, implement a one-time CLI command that creates the first administrator using credentials supplied through environment variables or securely prompted input. The command must refuse to create a second initial administrator if one already exists. Never seed a default password, expose an admin-creation HTTP endpoint, or commit credentials. Document the bootstrap procedure in README. If a future deployment uses an existing identity provider, replace this bootstrap mechanism deliberately rather than silently.

### 19.3 Class and section model

Use explicit database records rather than free-text values in assignment checks:

- `classes`: stable class identifier and display name/code.
- `sections`: stable section identifier, section code/name, and owning class foreign key.
- `educator_class_assignments`: educator ID, class ID, optional section ID, active flag, created-by administrator ID, created timestamp, and optional revoked timestamp.
- `students`: add or reference the student's class and section using foreign keys, if those relationships are not already present. Enforce that a student's section belongs to the same class.

Assignment semantics:
- An assignment with a `section_id` grants access only to that section.
- An assignment with `section_id = null` grants access to all sections of the specified class. This broader grant must be explicit and visible to the administrator.
- Multiple assignments are allowed. Duplicate active assignments must be prevented by a suitable database constraint or transactional service check.
- Unknown or unassigned class/section IDs must be rejected.
- Do not infer assignments from educator email domains, student names, request parameters, or frontend state.

If the source dataset or product brief does not define how classes/sections are initially populated, provide a documented seed/import path and mark the source of those records as a deployment decision. Do not invent real student records.

### 19.4 Educator capabilities and response boundaries

Educators can:
- View the list of classes/sections currently assigned to them.
- View aggregate learning analytics for an assigned scope, derived from existing MindMesh sessions and diagnosis snapshots.
- Drill down to an individual student's diagnosis, evidence, likely cause, readiness, learning progress, and relevant history, but only when that student currently belongs to an assigned scope.
- See uncertainty and evidence limitations exactly as the student diagnosis engine records them.

Educators cannot:
- Register or promote themselves as administrators.
- Approve other educators or modify assignments.
- Read students outside their assignments by changing a URL, query parameter, request body, or student ID.
- Alter a student's answers, evidence, diagnosis, mastery, readiness, snapshots, or learning path through analytics endpoints.
- Use an analytics request to trigger a new diagnosis, retest, or answer submission on behalf of a student unless a later requirement explicitly adds that capability.

Analytics must be derived from existing persisted records. Keep aggregate metrics simple and explainable for the MVP, for example:
- number of students in the authorized class/section;
- number with a completed diagnostic snapshot;
- counts of concepts by status (`mastered`, `confirmed_gap`, `suspected_gap`, `uncertain`, `unassessed`);
- common supported root gaps across the authorized students;
- progress/retest outcome summaries where data exists.

Define denominators and exclude students without relevant assessment data from rates rather than treating missing data as failure. Do not present heuristic mastery estimates as calibrated probabilities, and do not claim educational accuracy. Aggregates must be computed only after the authorized student set is determined in the backend.

### 19.5 Proposed educator/admin API endpoints

All endpoints live under `/api/v1`. These are new v3 endpoints; retain existing student routes and contracts unless an implementation issue is demonstrated and documented.

- `POST /educators/register` — create a pending educator account; never accept a role or approval state from the client.
- `GET /educators/me` — return the authenticated educator's own profile and activation status.
- `GET /educators/me/assignments` — list active class/section assignments for the authenticated educator.
- `GET /educators/me/classes/{class_id}/analytics` — return aggregate analytics only if the educator has active access to that class. If section-scoped analytics are requested, require and validate the section scope.
- `GET /educators/me/students` — list only students in the educator's current assignments; support validated pagination and optional class/section filters that can narrow, never broaden, the authorized set.
- `GET /educators/me/students/{student_id}/diagnosis` — return the student's latest finalized diagnosis and supported evidence only after a server-side assignment check.
- `GET /educators/me/students/{student_id}/progress` — return relevant session, retest outcome, epoch/trend, and learning progress information only after the same assignment check.

Administrator endpoints (all require administrator role):
- `GET /admin/educators?status=pending` — list educator accounts for review.
- `POST /admin/educators/{educator_id}/approve` — approve an eligible pending educator.
- `POST /admin/educators/{educator_id}/suspend` — suspend/revoke access.
- `POST /admin/educators/{educator_id}/assignments` — create an assignment to an existing class and optional section.
- `DELETE /admin/educators/{educator_id}/assignments/{assignment_id}` — revoke an assignment.
- `GET /admin/educators/{educator_id}/assignments` — inspect assignments.

Use request/response schemas with explicit fields. Do not return password hashes, token material, internal secrets, or unrelated student data. Use consistent error envelopes from section 11.13. Apply pagination to lists and sensible limits to event/log payloads.

### 19.6 Authorization implementation requirements

- Implement reusable dependencies such as `get_current_identity`, `require_student`, `require_educator`, and `require_admin`, adapted to the chosen auth design.
- Implement a single service/helper that resolves the authorized student IDs for an educator and requested class/section scope. Use it for both aggregate analytics and individual drill-down.
- Enforce access in service/repository queries, not only in route handlers or frontend visibility.
- Every educator student-detail request must verify the student's current class and section against the educator's active assignments in the same request transaction or query.
- Avoid fetching unauthorized records first and filtering them in Python after the fact.
- Use short-lived access tokens or otherwise ensure role/status/assignment revocation is checked against current server-side state. Document token expiration and refresh behavior.
- Record security-relevant administrator actions (approval, suspension, assignment creation/revocation) with actor ID, target ID, action, timestamp, and minimal metadata. Do not log passwords, bearer tokens, or student diagnosis payloads.
- Keep student and educator identity tables logically distinct unless the implementation has a clear, documented reason to unify them. If identities are unified, enforce role boundaries with database and service-level constraints.

### 19.7 v3 database additions

Add SQLAlchemy models and Alembic migrations for the necessary entities, adapting names if equivalent structures already exist:

- `educators`: ID, normalized unique email, password hash or external identity reference, display name, status (`pending`, `approved`, `rejected`, `suspended`), created/updated timestamps, approved-by administrator ID and approval timestamp where applicable.
- `administrator_accounts` or a documented administrator role on a protected identity model.
- `classes`.
- `sections`: foreign key to `classes`.
- `educator_class_assignments`: educator, class, optional section, active/revocation metadata, creator administrator.
- `admin_audit_events`: actor, action, target type/ID, timestamp, minimal metadata.
- Add class/section foreign keys to students if absent.

Use foreign keys, indexes for common authorization filters, unique constraints, and appropriate delete behavior. Prefer revocation/soft-deactivation for assignments over deleting audit history. Do not cascade-delete assessment history when an educator is suspended or an assignment is revoked. Migrations must be reversible where practical and must not drop or rewrite existing student assessment data.

### 19.8 v3 acceptance and security tests

Add tests proving all of the following:

- Educator registration always creates `pending` status and cannot set `approved`, `administrator`, or arbitrary role values.
- Pending, rejected, and suspended educators receive no class list, analytics, student list, diagnosis, or progress data.
- An approved educator with no assignment still receives no student data.
- An educator assigned to Section A cannot read Section B, another class, or a student who changes section to an unassigned scope.
- A class-wide assignment works only when explicitly created with no section scope.
- Query parameters, path IDs, and body fields cannot broaden the educator's authorized student set.
- Removing an assignment or suspending an educator blocks access on the next request, including with a previously issued token.
- An educator cannot access administrator endpoints or modify assignments.
- A student cannot access educator or administrator endpoints.
- One educator cannot see another educator's private profile or assignment management data.
- Analytics aggregates use only authorized students and correct denominators; no-data cases are represented honestly.
- Individual drill-down returns only the fields permitted by the endpoint and does not leak other students' information.
- SQL/database constraints prevent duplicate assignments and invalid class-section relationships.
- Student authentication, consent, diagnosis, evidence, mastery, replay, retest, and selection acceptance tests from v1.2 continue to pass.

### 19.9 Implementation sequence for Antigravity

Build in small, verifiable phases. Do not generate the entire application in one pass.

1. **Foundation:** inspect the workspace, create the backend structure, pinned dependencies, settings, database connection, Alembic, health endpoint, and tests.
2. **Curriculum and graph:** seed the eight concepts and reviewed question/resource data; validate graph and content at startup.
3. **Deterministic engine:** signals, evidence, mastery, epochs, replay; unit tests before APIs.
4. **Student sessions:** authentication, consent, sessions, events, answers, selector, finalization, snapshots.
5. **Student learning APIs:** graph, diagnosis, feedback, concept detail, resources, hints, practice, retest, report.
6. **Educator/admin identity:** password hashing, registration, one-time administrator bootstrap, approval/suspension, role dependencies.
7. **Assignments and isolation:** class/section models, assignment management, centralized scope authorization, revocation tests.
8. **Educator analytics and drill-down:** aggregates and individual views using only authorized records.
9. **Hardening:** transaction/idempotency behavior, migrations, API edge cases, audit events, security tests, README, simulated journeys.
10. **Optional LLM:** only after deterministic behavior and all required tests pass; it must remain disabled by configuration and cannot control diagnosis.

At the end of each phase, report changed files, commands actually run, exact test results, unresolved issues, and the next phase. Never claim a test passed unless it was executed.

---

## 20. Antigravity master prompt for v3

Implement MindMesh Backend Specification v3.0 in the current workspace, one phase at a time. First inspect the workspace and report its structure; do not overwrite existing work. If the workspace is empty, initialize the backend using the structure and stack in this specification.

Follow v1.2's deterministic diagnosis, evidence, mastery, selection, reason, prerequisite, and retest rules exactly. Educator access is a separate authorization layer: educators self-register as pending, an administrator approves them and assigns classes/sections, and educators can access only currently assigned scopes. Implement secure one-time initial-admin bootstrap without a public admin-registration endpoint or default credentials. Enforce authorization in backend queries/services on every request, not only in the frontend. Revocation must take effect on the next request.

Do not invent curriculum content, student records, credentials, thresholds, or claims of accuracy. Seed only reviewed, clearly identified sample curriculum/questions needed for local development; if complete reviewed content is unavailable, mark it as a content gap and do not pretend the question bank satisfies acceptance requirements. Keep all thresholds in `settings_rules.py`. The LLM is optional and must never decide correctness, evidence, mastery, status, likely causes, roots, readiness, graph edges, or question selection.

Start with Phase 1 only. Before coding, list the planned files and the smallest complete implementation slice. Then implement, run available tests/lint/type checks, and report exact results. Do not proceed to Phase 2 until the Phase 1 result is reported and the user approves continuation.

## 21. v3 assumptions and unresolved deployment decisions

- **Initial administrator creation:** this spec proposes a one-time CLI bootstrap; confirm this is acceptable for the deployment environment.
- **Class/section source:** the organization must decide whether class/section records and student memberships are imported, seeded for a demo, or synchronized from another system.
- **Student identity onboarding:** v1.2 specifies minimal bearer-token auth but does not fully define student registration/login/token issuance. Implement a clearly documented MVP auth flow without weakening student isolation; confirm any production identity-provider choice separately.
- **Educator identity verification:** administrator approval is the MVP verification gate. Institutional email verification or external identity integration is not assumed.
- **Analytics definitions:** implement only the metrics listed in 19.4 initially; any additional metric needs an explicit definition and denominator.
- **Content readiness:** the specification requires at least four reviewed diagnostic questions per concept and recommends five total per concept, including held-out retest items. Do not invent unreviewed questions and label them reviewed.
- **Privacy and retention:** deploy only with an approved policy for student consent, retention, and access to educational records. Do not use real student data in sample seeds or tests.

---

## 15. Completion checklist

- [ ] Graph loads and passes DAG validation
- [ ] Question bank seeded to the chosen size (4 or 5 per concept) with mapped distractors, `expected_time_s`, and held-out retest items
- [ ] Consent and 12-question cap enforced
- [ ] Events and final answers reliable and idempotent; timing and signals server-side
- [ ] Estimates and statuses deterministic and replayable (including epochs)
- [ ] Three-question confirmation, readiness, and precedence rules implemented
- [ ] Reason tags and likely cause implemented with templates
- [ ] Prerequisite probe, need-based retest, and `ready` gating implemented
- [ ] Selector and root-gap ranking tested; selection log stored
- [ ] Feedback, graph, concept-detail APIs working
- [ ] Hints only in practice
- [ ] Retest fresh, with honest outcome labels
- [ ] Insufficient evidence displayed honestly
- [ ] LLM can be disabled
- [ ] Unit, API, integration, simulation tests pass
- [ ] README: setup, env vars, seed command, test command, limitations

---

## 16. Implementation order

Use the v3 phased implementation sequence in section 19.9. Do not implement the full system in one generation; complete and verify one phase at a time.

---

## 17. Master instruction for a coding assistant

Use the full v3 Antigravity master prompt in section 20. The assistant must inspect the workspace first, implement Phase 1 only, run tests, and report exact results before continuing.

---

## 18. Limitations (v1.2 engine and v3 access layer)

- Mastery is a heuristic estimate, not a calibrated probability.
- Thresholds and signal weights are conservative MVP values, not validated educational thresholds.
- Option-change events come from the client and can be lost or spoofed; their effect is bounded but not zero.
- Reason tags and likely causes describe observed behaviour; they are not proof of what the student was thinking.
- A 12-question session may not confirm every gap.
- With 4 questions per concept, a confirmed gap can be retested once and cannot be verified as mastered; 5 per concept is recommended. Each concept supports one retest cycle in the MVP.
- Practice mostly re-serves diagnostic items, which add no evidence; a separate practice bank is future work.
- The graph simplifies some real DBMS prerequisites (notably D09).
- Passing tests proves rule compliance, not diagnostic accuracy or learning gains.
- Educator analytics are limited to the assigned class/section scopes and the metrics defined in section 19.4; broader school-wide analytics are not part of this MVP.
- Secure educator access depends on correct student class/section membership data. Incorrect or stale membership data can produce incorrect access decisions, so import/update procedures must be controlled and tested.
