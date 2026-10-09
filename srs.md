# Software Requirements Specification (SRS)

## MIND MESH: Adaptive Learning Dependency Graph (Subject: DBMS)

| | |
|---|---|
| **Event** | AI-VERSE, Problem Statement 30: Adaptive Learning Dependency Graph |
| **Version** | 1.0 (hackathon MVP) |
| **Subject domain** | Database Management Systems (DBMS), 18 concepts |
| **SDGs** | SDG 4 (Quality Education), SDG 9 (Industry, Innovation, Infrastructure), SDG 10 (Reduced Inequalities) |

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for MIND MESH, a web application that traces a student's wrong answers to the missing foundational concept behind them, then reorders study material so that gap is fixed first.

### 1.2 Problem Statement
- Scores hide *why* a student struggles.
- When the cause is a **missing prerequisite**, more practice on the failing topic does not help.
- Teachers cannot check every student's foundations at scale.

A student may score well on familiar SQL queries yet fail a normalization question. Conventional platforms respond with more normalization practice, but the real blocker may be *functional dependencies* or *keys*.

### 1.3 Scope
**In scope (MVP):**
- One subject: DBMS, with **18 concepts** in a prerequisite graph.
- A diagnostic quiz with a **maximum of 12 questions per session**, drawn from **36 prewritten questions** (2 per concept).
- Root-gap detection, a reordered learning path, and a before/after report.
- A teacher view showing a class-level gap heatmap.

**Out of scope:** multiple subjects, a general chatbot or AI tutor, full LMS features (assignments, grading, messaging), real-world learning-effectiveness claims, and mobile apps.

### 1.4 Definitions

| Term | Meaning |
|---|---|
| **Concept** | A node in the graph, e.g. "Functional Dependencies". |
| **Prerequisite edge** | `A → B` means *A must be learned before B*. This direction is used everywhere. |
| **Mastery estimate (p)** | A heuristic value between 0 and 1 per student-concept. It is **not** a calibrated probability. |
| **Root gap** | The prerequisite concept that best explains a student's failure on a dependent concept, per the rules in section 5. |
| **Suspected gap** | Evidence hints at a weakness but the confirmation rule is not yet met. |
| **Confirmed gap** | The confirmation rule in section 5.3 is met. |
| **Insufficient evidence** | Not enough evidence to call mastery or weakness. |
| **Direct evidence** | An answer on a question tagged to the concept, or a selected distractor mapped to a misconception about that concept. |
| **Rule-based fallback** | Fully deterministic operation that works with no LLM available. |

---

## 2. Overall Description

### 2.1 Product Perspective
MIND MESH is a standalone web application: a Next.js frontend, a FastAPI backend that holds the engine, and a PostgreSQL database.

```
Student ──► Diagnostic Quiz ──► Responses (choice, confidence, time)
                                     │
                                     ▼
                           Graph Engine updates mastery
                                     │
                                     ▼
                         Root-gap detection (rules)
                                     │
                                     ▼
              Reordered learning path ──► Retest ──► Before/After report
```

### 2.2 Core Loop
**Assess → Estimate mastery → Diagnose → Verify → Adapt → Reassess**

### 2.3 User Classes

| User | Needs |
|---|---|
| **Student** | Take the quiz, see the root gap with an explanation, follow a short path, see improvement. |
| **Teacher / Evaluator** | See which foundational concepts the class is missing and inspect the evidence behind a diagnosis. |

### 2.4 Design Principles
1. **The diagnosis is deterministic and explainable.** The graph and rules decide the root gap, not an LLM.
2. **The LLM assists but never decides.** It may rank among candidates the engine already approved, draft question variants, and write explainers (see 7.3).
3. **Evidence is stored.** Every diagnosis can be reproduced from stored responses.
4. **No false certainty.** One wrong answer never confirms a gap, and one right answer never proves mastery.

### 2.5 Assumptions and Constraints
- Single subject (DBMS), 18 concepts, 36 prewritten questions, max 12 questions per session.
- The prerequisite graph is hand-curated and validated at startup.
- Mastery parameters (guess, slip, thresholds) are documented defaults, **not fitted to real learner data**.
- Delivered as a hackathon MVP in a very short build window.

---

## 3. DBMS Concept Graph (18 concepts)

### 3.1 Concepts

| ID | Concept | Prerequisites |
|---|---|---|
| D01 | DBMS Basics (data, schema, architecture) | none |
| D02 | Relational Model (tables, tuples, attributes) | D01 |
| D03 | Keys (super, candidate, primary, foreign) | D02 |
| D04 | Integrity Constraints | D02, D03 |
| D05 | ER Modeling | D01 |
| D06 | ER-to-Relational Mapping | D05, D03 |
| D07 | Relational Algebra | D02 |
| D08 | SQL Basics (DDL, SELECT, WHERE) | D02 |
| D09 | SQL Joins | D08, D07 |
| D10 | Aggregation and GROUP BY | D08 |
| D11 | Subqueries and Views | D08, D09 |
| D12 | Functional Dependencies | D03 |
| D13 | Normalization (1NF to 3NF) | D12, D03 |
| D14 | BCNF and Decomposition | D13 |
| D15 | Transactions and ACID | D01 |
| D16 | Concurrency Control (locks, serializability) | D15 |
| D17 | Indexing (B+ trees) | D03, D08 |
| D18 | Query Processing and Optimization | D07, D09, D17 |

### 3.2 Graph Diagram

```
D01 ─► D02 ─► D03 ─► D04
 │      │      ├────► D06 ◄── D05 ◄── D01
 │      │      ├────► D12 ─► D13 ─► D14
 │      │      └────► D17 ─┐
 │      ├────► D07 ───┐    │
 │      └────► D08 ───┼─► D09 ─► D11
 │               ├────► D10    │
 │               └────► D17    └──► D18 ◄── D07, D17
 └────► D15 ─► D16
```

### 3.3 Graph Requirements
- The graph is a directed acyclic graph (DAG). It is validated on load (see FR-G2).
- A concept may have several prerequisites, and a student may be missing any subset of them.
- Each concept stores: `id`, `name`, `description`, `difficulty (1-5)`, `learning_objectives`, `prerequisites[]`, and `resources[]`.

---

## 4. Question Bank

### 4.1 Size and Structure
- **36 prewritten multiple-choice questions**: two per concept, labelled family A and family B.
- Every question has 4 options, one correct answer, and a difficulty rating.
- Each question is tagged to one **primary concept** and optionally one **secondary concept**.

### 4.2 Options Mapped to Concepts
Each **wrong option (distractor)** is mapped to a *misconception* tied to a specific concept, usually a prerequisite. Choosing a distractor is therefore direct evidence about that concept.

**Example (D13 Normalization, primary concept):**

```json
{
  "id": "Q13A",
  "concept": "D13",
  "family": "A",
  "difficulty": 3,
  "prompt": "R(A,B,C) with FDs: A→B, B→C. Key is A. Which normal form is R in?",
  "options": [
    {"id": "a", "text": "3NF",  "correct": false, "maps_to": "D13", "misconception": "Ignores transitive dependency B→C"},
    {"id": "b", "text": "2NF but not 3NF", "correct": true},
    {"id": "c", "text": "1NF only", "correct": false, "maps_to": "D12", "misconception": "Cannot read FDs / confuses dependency direction"},
    {"id": "d", "text": "BCNF", "correct": false, "maps_to": "D03", "misconception": "Cannot identify the key from FDs"}
  ],
  "explanation": "A is the key. B→C is a transitive dependency, so R is 2NF but not 3NF.",
  "validation_status": "reviewed"
}
```

### 4.3 Question Rules
- Every concept must have at least 2 questions from different families (checked at startup).
- Every distractor with a `maps_to` must reference a valid concept.
- Question text is reviewed by a human before use.

---

## 5. Mastery Estimation and Gap Rules

All numbers in this section are **documented defaults**. They are heuristic and uncalibrated, and must be shown as "estimate", never as a validated probability.

### 5.1 Mastery Representation
For each student and concept, the system stores:
- `p` (mastery estimate, 0 to 1, initial value 0.5),
- `n_direct` (count of direct evidence events),
- `n_indirect` (count of propagated evidence events).

A concept is **uncertain** when `n_direct < 2` or `0.35 ≤ p ≤ 0.65`.

### 5.2 Update Rule (per answer)
1. **Bayesian step.** Using guess `g = 0.25` and slip `s = 0.10` (MCQ defaults), compute `p_bayes` from the answer's correctness.
2. **Evidence weight `w`.** Start at 1.0 and adjust using the confidence tap and response time:
   - Correct with low confidence: `w = 0.6` (likely a guess).
   - Wrong with high confidence: `w = 1.2` (likely a misconception).
   - Answer in under 3 seconds: `w × 0.7`.
3. **Apply:** `p_new = p + w × (p_bayes − p)`, clamped to 0.02 to 0.98.
4. **Distractor evidence.** A wrong answer that selects a mapped distractor applies a weight-0.5 update to the mapped concept.
5. **Propagation to prerequisites.** A wrong answer on concept X applies a small update (factor 0.3) to each direct prerequisite of X, counted as **indirect** evidence. A correct answer on X applies a smaller upward update (factor 0.15).

Indirect evidence **raises uncertainty or marks a suspect**. It can never by itself confirm a gap.

### 5.3 Gap Status Rules

| Status | Rule |
|---|---|
| **Insufficient evidence** | `n_direct < 2` and not suspected. |
| **Suspected gap** | A dependent concept was failed, and the prerequisite has `p < 0.5` or is uncertain. |
| **Confirmed gap** | `p < 0.30` **and** at least 2 direct evidence events from 2 *different questions*. |
| **Rejected (not a gap)** | `p > 0.70` and `n_direct ≥ 2`. |

If evidence stays inconclusive after the question budget, the concept is reported as **uncertain**, and the path includes a low-cost review without assuming mastery.

### 5.4 Root-Gap Selection
Among confirmed (or, failing that, suspected) gaps in the ancestors of the failed concept, choose the one with the highest `blocker_score`:

`blocker_score = (1 − p) × importance`

where `importance` is the share of the student's target concepts that depend on it (directly or transitively). Ties go to the **deepest prerequisite** (closest to the foundations).

---

## 6. Functional Requirements

### 6.1 Concept Graph Engine

| ID | Requirement | Priority |
|---|---|---|
| FR-G1 | Load the concept graph from a JSON/YAML file and expose prerequisites and dependents. | Must |
| FR-G2 | Validate on startup: no cycles, no dangling prerequisite IDs, no self-edges, no orphan concepts. The app must refuse to start on an invalid graph and report why. | Must |
| FR-G3 | Return all ancestors (foundational prerequisites) of a concept, with distance. | Must |
| FR-G4 | Return a valid learning order (topological sort) for any set of concepts. | Must |
| FR-G5 | Compute `importance` for each concept (descendant coverage). | Must |
| FR-G6 | Provide graph data for visualization (nodes with mastery state, edges). | Must |

### 6.2 Diagnostic Module

| ID | Requirement | Priority |
|---|---|---|
| FR-D1 | Show a consent screen before the first question; no quiz data is stored without consent. | Must |
| FR-D2 | Present one MCQ at a time with a **confidence tap** (Not sure / Fairly sure / Sure) and measure response time. | Must |
| FR-D3 | Enforce a maximum of **12 questions per session**. | Must |
| FR-D4 | **Adaptive question choice:** rank candidate questions by `uncertainty(p) × importance`, where `uncertainty(p) = 1 − |2p − 1|`; never repeat a question in one session. | Must |
| FR-D5 | Session phases: baseline probes (up to 4, spread across the graph), targeted diagnosis (up to 6), verification (up to 2). Unused budget carries forward. | Should |
| FR-D6 | Record every response with option, correctness, confidence, time, and timestamp. | Must |
| FR-D7 | After a failure on a concept, add its prerequisites as diagnostic candidates (ancestors within depth 2). | Must |

### 6.3 Graph Engine and Diagnosis

| ID | Requirement | Priority |
|---|---|---|
| FR-M1 | Update mastery after **each answer** using the rules in 5.2. | Must |
| FR-M2 | Apply distractor-mapped evidence and prerequisite propagation as in 5.2. | Must |
| FR-M3 | Assign each concept a status (insufficient, suspected, confirmed, rejected) using 5.3. | Must |
| FR-M4 | Select the root gap using 5.4 and generate a plain-language explanation citing the specific answers used. | Must |
| FR-M5 | **Rule-based fallback:** if the LLM is unavailable, slow (more than 3 s), or returns an invalid result, the engine continues using only deterministic rules with no loss of core function. | Must |
| FR-M6 | Never mark a concept confirmed or mastered from a single response. | Must |

### 6.4 Path and Report Module

| ID | Requirement | Priority |
|---|---|---|
| FR-P1 | Generate a learning path: the root gap and any other confirmed gaps, plus the failed concept, in topological order. Skip concepts with `p > 0.70` and `n_direct ≥ 2`. | Must |
| FR-P2 | Each path item shows a one-line reason, e.g. "Recommended because answers on Q13A and Q12B suggest difficulty with Functional Dependencies, which Normalization requires." | Must |
| FR-P3 | If a concept has no learning resource, show a clear placeholder rather than failing. | Must |
| FR-P4 | After the student completes a path item, run a **retest** using a different question from the concept's other family, then re-check the originally failed concept. | Must |
| FR-P5 | Show a **before/after report**: mastery estimates, root-gap status, and quiz result before vs. after. | Must |
| FR-P6 | Recompute the path whenever new evidence arrives. | Should |
| FR-P7 | **Teacher gap heatmap:** a class-level grid of concepts by share of students with a suspected or confirmed gap, with drill-down to individual evidence. | Should |

### 6.5 Interface

| ID | Requirement | Priority |
|---|---|---|
| FR-U1 | Show the concept graph with color-coded mastery (e.g. green strong, amber uncertain, red gap) and a distinct marker for suspected vs. confirmed. | Must |
| FR-U2 | Show an uncertainty indicator on each node. | Should |
| FR-U3 | Show an explanation panel listing the evidence behind a diagnosis. | Must |
| FR-U4 | Show a progress summary: quiz score, concept mastery summary, root-gap concept, and personalized study order. | Must |

---

## 7. AI/LLM Component

### 7.1 Role
The engine is **deterministic rules plus a live LLM**. The LLM is an assistant, not the decision-maker.

### 7.2 Permitted LLM Uses
1. **Generate question variants**, reworded versions of prewritten questions (same concept tag, same answer key).
2. **Help choose the next question** by re-ranking the top 3 candidates the deterministic ranker already approved.
3. **Write explainers and practice items** for the learning path.

### 7.3 Guardrails
- The LLM **cannot** change mastery values, gap status, root-gap selection, or prerequisite edges.
- Question selection from the LLM must be one of the engine's top-3 candidates. Anything else is discarded.
- LLM-generated variants are tagged `llm_generated`. They are used only for **practice and explainers** unless they pass validation (valid schema, exactly one correct option, concept tags unchanged); only validated variants may serve as verification items (see 11.2).
- Every LLM call has a timeout and falls back to the deterministic path (FR-M5).
- LLM output shown to students is labelled as generated explanation content.
- No student-identifying information is sent to the LLM.

---

## 8. Data Model (PostgreSQL)

| Table | Key fields |
|---|---|
| `concepts` | id, name, description, difficulty, objectives |
| `prerequisite_edges` | source_concept_id, target_concept_id |
| `questions` | id, concept_id, family, difficulty, prompt, correct_option, explanation, validation_status, origin (`prewritten` or `llm_generated`) |
| `question_options` | question_id, option_id, text, is_correct, maps_to_concept_id, misconception |
| `students` | id (pseudonymous), consent_given_at, role |
| `sessions` | id, student_id, kind (`diagnostic` or `retest`), started_at, ended_at |
| `responses` | id, session_id, question_id, option_id, correct, confidence, response_ms, answered_at |
| `student_concept_mastery` | student_id, concept_id, p, n_direct, n_indirect, status, updated_at |
| `gap_diagnoses` | id, student_id, concept_id, status, evidence_summary, rationale, created_at, resolved_at |
| `learning_paths` / `learning_path_items` | path id, student, position, concept_id, rationale, completion_status |

The mastery table can be rebuilt from `responses`. Responses are the source of truth, and the diagnosis rationale references the response IDs it used.

---

## 9. API (FastAPI)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/sessions` | Start a diagnostic or retest session (requires consent) |
| GET | `/sessions/{id}/next` | Next question, chosen per FR-D4 |
| POST | `/sessions/{id}/answer` | Submit option, confidence, time; returns updated mastery |
| GET | `/students/{id}/graph` | Graph with mastery and gap status |
| GET | `/students/{id}/diagnosis` | Root gap and evidence explanation |
| GET | `/students/{id}/path` | Reordered learning path |
| POST | `/path/items/{id}/complete` | Mark a path item as studied and unlock the retest |
| GET | `/students/{id}/report` | Before/after report |
| GET | `/teacher/heatmap` | Class gap heatmap (teacher role only) |

All inputs are validated, and invalid requests return clear error responses. Students can access only their own records, and the teacher endpoints require the teacher role.

---

## 10. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Performance | The next question appears in under 2 seconds with a deterministic choice. With the LLM, fall back after 3 seconds. |
| NFR-2 | Explainability | Every root-gap claim shows the evidence and answers it relied on. |
| NFR-3 | Reliability | Core diagnosis works fully with the LLM disabled. |
| NFR-4 | Privacy | Collect no unnecessary personal data. Use pseudonymous student IDs, show a consent screen, and send no identifying data to the LLM. |
| NFR-5 | Security | Backend authorization for all student and teacher data. No secrets in the repository. |
| NFR-6 | Usability | A student can complete a session without instructions. Technical terms are kept off the student view. |
| NFR-7 | Reproducibility | A single documented command (or short sequence) starts the app locally. Environment variables are documented. |

---

## 11. Demo Scenario and Evaluation

### 11.1 Demo Scenario (must be produced by the engine, not hardcoded)
1. The student answers SQL Basics (D08) and Selection questions correctly.
2. They are shown a Normalization question (D13) and answer wrongly with **high confidence**.
3. The engine marks D13 weak and lists D12 (FDs) and D03 (Keys) as suspects.
4. It asks a targeted question on D12 rather than more normalization practice.
5. The answers confirm a gap on D12 according to rule 5.3; D03 is rejected or stays uncertain.
6. The system shows the root gap, the evidence, and a short path: D12 then D13.
7. After studying D12, the student takes a retest question from the other family, then a fresh D13 question.
8. The before/after report shows the change in estimates.

To run this reliably in front of judges, use a **seeded demo student profile** that answers according to a known hidden gap. The engine must still compute everything from the responses.

### 11.2 Question-Bank Limitation
With only 2 questions per concept, the second question is used for the retest, and confirming a gap with two direct events may require distractor-mapped evidence from other questions. If a verification question is not available for a concept, the system uses a validated LLM variant (tagged) or reports "verification limited". **If time allows, expand the bank to 3 questions per concept (54).**

### 11.3 Evaluation (secondary, if time allows)
Run a seeded simulation of students with known hidden gaps, and compare:
- **Baseline A:** fixed curriculum order.
- **Baseline B:** lowest-scoring topic first.
- **Proposed:** MIND MESH prerequisite-aware diagnosis.

Report diagnostic precision, recall, and questions-to-diagnosis, and state plainly that simulated results validate algorithm behavior only. **They do not establish real-world educational effectiveness.**

---

## 12. Acceptance Criteria and Tests

| ID | Check |
|---|---|
| T1 | A graph containing a cycle is rejected at startup. |
| T2 | A dangling prerequisite ID is rejected. |
| T3 | Topological order always places prerequisites before dependents. |
| T4 | A single wrong answer does **not** produce a confirmed gap. |
| T5 | A single correct low-confidence answer does **not** set `p` above 0.70. |
| T6 | Two direct pieces of evidence from different questions with `p < 0.30` produce a confirmed gap. |
| T7 | The next question is never repeated within a session, and no session exceeds 12 questions. |
| T8 | With the LLM disabled, the full demo scenario still completes. |
| T9 | The path never includes a concept with `p > 0.70` and `n_direct ≥ 2`. |
| T10 | The path recomputes after new evidence. |
| T11 | A student cannot read another student's data. |
| T12 | A concept with no learning resource still appears in the path with a placeholder. |
| T13 | Distractor-mapped evidence updates the mapped concept. |

---

## 13. Build Priorities

1. Graph loader, validator, and tests (T1 to T3).
2. Question bank (36 items) and the distractor mapping.
3. Mastery update, status rules, and root-gap selection (T4 to T6, T13).
4. Question selector and the session flow (T7).
5. Path generation and retest (T9 to T10).
6. Graph UI, explanation panel, before/after report.
7. LLM assistance with the deterministic fallback (T8).
8. Teacher heatmap, then the simulation evaluation.

If time runs short, cut in this order: evaluation, heatmap, LLM question variants, uncertainty indicators. **Do not cut** the retest and the evidence panel.

---

## 14. Risks and Limitations

| Risk | Mitigation |
|---|---|
| Thresholds and parameters are not calibrated | Label values as estimates; keep them in one config file; document them |
| Only 2 questions per concept limits confirmation and verification | Distractor evidence, validated variants, and a stretch goal of 54 questions |
| LLM output may be wrong or inconsistent | Guardrails in 7.3 and the deterministic fallback |
| Very short sessions give little evidence | Report "uncertain" honestly instead of forcing a verdict |
| Hand-curated graph may contain debatable prerequisite links | Document the edge rationale and let a teacher review |
| No real learner study | State this limitation in the demo and the README |
