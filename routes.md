# MindMesh — Complete Application Routes & Real Data Connection Guide

This document maps all **Frontend Page Routes**, **Backend API Endpoints**, and their **Real Data Connections** across the MindMesh architecture.

---

## 🧭 1. Frontend Page Routes (Next.js App Router)

| Route Path | Page Component | Purpose | Auth Required | Primary API Endpoints Connected |
|---|---|---|---|---|
| `/` | `app/page.tsx` | Main application shell & entry point | Yes (redirects to `/signin` if unauthenticated) | `/api/concepts`, `/api/questions` |
| `/signin` | `app/signin/page.tsx` | Dedicated authentication page for Student & Educator | No | Local auth state / session tokens |
| `/signup` | `app/signup/page.tsx` | Account registration for new learners and educators | No | Local auth state / session tokens |
| `/dashboard` | `app/dashboard/page.tsx` | Role-based dashboard (Student stat strip or Educator portal) | Yes | `/api/concepts`, `/api/cohort` |
| `/quiz` | `app/quiz/page.tsx` | Diagnostic Quiz (Consent screen, confidence rating, response timer) | Yes | `GET /api/questions?family=A`<br>`POST /api/diagnose` |
| `/diagnosis` | `app/diagnosis/page.tsx` | Interactive 18-concept DAG graph and evidence drawer | Yes | `GET /api/graph`<br>`POST /api/diagnose` |
| `/sources` | `app/sources/page.tsx` | Remediated learning path & curated external links | Yes | `POST /api/roadmap` |
| `/retest` | `app/retest/page.tsx` | Family B verification retest and Before/After mastery report | Yes | `GET /api/questions?family=B`<br>`POST /api/diagnose` |
| `/educator` | `app/educator/page.tsx` | 24-student class cohort heatmap and strategy benchmarks | Yes (Educator) | `GET /api/cohort`<br>`GET /api/graph` |
| `/profile` | `app/profile/page.tsx` | User identity, academic progress, role mode switcher & account settings | Yes | `/api/concepts`, local session |

---

## ⚡ 2. Real Data API Routes (`/api/...`)

All data routes are implemented in `frontend/app/api/...` and proxy to the Python **NetworkX FastAPI** service (`http://localhost:8000`), with canonical fallback persistence in `frontend/data/`.

### `GET /api/concepts`
- **File**: `frontend/app/api/concepts/route.ts`
- **Description**: Returns all 18 DBMS concepts, difficulty levels, prerequisites, learning objectives, and resources.
- **Backend Service**: `http://localhost:8000/api/concepts`
- **Response**:
  ```json
  [
    {
      "id": "D12",
      "name": "Functional Dependencies",
      "difficulty": 3,
      "prerequisites": ["D03"],
      "learning_objectives": ["Define functional dependencies", "Compute attribute closure X+"],
      "resources": [...]
    }
  ]
  ```

---

### `GET /api/questions`
- **File**: `frontend/app/api/questions/route.ts`
- **Query Parameters**:
  - `family`: Filter by question family (`A` for initial diagnostic, `B` for retest).
  - `concept`: Filter by concept ID (e.g., `D12`, `D13`).
- **Backend Service**: `http://localhost:8000/api/questions`
- **Response**: List of 36 validated diagnostic questions with distractors and misconception mappings.

---

### `GET /api/graph`
- **File**: `frontend/app/api/graph/route.ts`
- **Description**: Returns the Directed Acyclic Graph structure, topological ordering, and transitive reduction edges computed by NetworkX.
- **Backend Service**: `http://localhost:8000/api/graph`
- **Response**:
  ```json
  {
    "nodes": [
      { "id": "D01", "name": "DBMS Basics", "in_degree": 0, "out_degree": 3, "importance": 0.94 }
    ],
    "edges": [
      { "source": "D01", "target": "D02" },
      { "source": "D12", "target": "D13" }
    ],
    "transitive_reduced_edges": [...],
    "topological_order": ["D01", "D05", "D02", "D03", "D07", "D08", "D12", "D13", ...],
    "is_valid_dag": true
  }
  ```

---

### `POST /api/diagnose`
- **File**: `frontend/app/api/diagnose/route.ts`
- **Description**: Submits quiz answers to the NetworkX engine to run Bayesian mastery parameter updates and root-gap isolation.
- **Backend Service**: `http://localhost:8000/api/diagnose`
- **Request Body**:
  ```json
  {
    "student_id": "alex-chen",
    "responses": [
      {
        "question_id": "Q13A",
        "concept_id": "D13",
        "option_id": "c",
        "confidence": "high",
        "response_ms": 1420
      }
    ]
  }
  ```
- **Response**:
  ```json
  {
    "target_failed_concept": "D13",
    "root_gap_id": "D12",
    "root_gap_name": "Functional Dependencies",
    "evidence_path": ["D12", "D13"],
    "confirmed_gaps": ["D12"],
    "suspected_gaps": ["D13"],
    "mastered": ["D01", "D02", "D08"],
    "explanation": "Failure on 'Normalization (1NF to 3NF)' was traced back via prerequisite DAG to foundational concept 'Functional Dependencies'."
  }
  ```

---

### `POST /api/roadmap`
- **File**: `frontend/app/api/roadmap/route.ts`
- **Description**: Generates a topologically ordered remediation sequence (`nx.topological_sort`) covering all identified gaps and missing prerequisites.
- **Backend Service**: `http://localhost:8000/api/roadmap`
- **Request Body**:
  ```json
  {
    "gap_ids": ["D12", "D13"]
  }
  ```
- **Response**:
  ```json
  {
    "ordered_concept_ids": ["D12", "D13"],
    "steps": [
      {
        "position": 1,
        "concept_id": "D12",
        "concept_name": "Functional Dependencies",
        "rationale": "Foundational requirement: Resolve before attempting dependent topics.",
        "estimated_mins": 15,
        "resources": [...]
      }
    ]
  }
  ```

---

### `GET /api/cohort`
- **File**: `frontend/app/api/cohort/route.ts`
- **Description**: Returns 24-student class cohort breakdown and simulation benchmarks across the 18 concepts.
- **Response**:
  ```json
  {
    "total_students": 24,
    "subject": "Database Management Systems (DBMS)",
    "cohort": [
      { "concept_id": "D12", "name": "Functional Dependencies", "confirmed_gaps": 11, "gap_rate": 64 }
    ],
    "benchmarks": [...]
  }
  ```

---

## 🔌 3. Where & How to Connect Real Data Routes

### In Frontend Code:
All API calls are centralized in [frontend/lib/apiClient.ts](file:///c:/work/hackthons/mindmesh/frontend/lib/apiClient.ts):
- `fetchConcepts()`: Calls `/api/concepts`
- `fetchQuestions(family)`: Calls `/api/questions`
- `fetchNetworkXGraph()`: Calls `/api/graph`
- `diagnoseWithNetworkX(responses)`: Calls `/api/diagnose`
- `fetchRoadmap(gapIds)`: Calls `/api/roadmap`
- `fetchCohortData()`: Calls `/api/cohort`

### Configuring External Backend:
If your backend runs on a remote server or port other than `8000`, set in `frontend/.env.local`:
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```
Or for production deployment (e.g. Vercel + Railway/Render):
```env
NEXT_PUBLIC_BACKEND_URL=https://api.yourdomain.com
```

### Connecting to a Real PostgreSQL Database:
In `backend/main.py` and `backend/graph_engine.py`, replace the JSON file loader with an async SQLAlchemy/Prisma connection:
```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/mindmesh")
```
The schemas in [backend/schemas.py](file:///c:/work/hackthons/mindmesh/backend/schemas.py) map 1:1 with PostgreSQL tables:
- `concepts` (id, name, difficulty, tier, prerequisites)
- `questions` (id, concept_id, family, prompt, explanation)
- `question_options` (id, question_id, text, correct, maps_to, misconception)
- `student_responses` (id, student_id, question_id, option_id, correct, confidence, response_ms)
- `student_mastery` (student_id, concept_id, p, n_direct, n_indirect, status)
