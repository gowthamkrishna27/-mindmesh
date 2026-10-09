# MindMesh Backend (v3.0)

MindMesh is an adaptive learning diagnostic assessment and learning system based on a deterministic concept dependency graph.

## Stack
- Python 3.12
- FastAPI + Uvicorn
- Pydantic v2
- SQLAlchemy 2.x + Alembic
- PostgreSQL (Production) / SQLite (Local dev & test)
- NetworkX (Graph validation & traversal)
- pytest + httpx (Testing)

## Curriculum & Dependency Graph (v3.0)

The focused DBMS curriculum models 8 core concepts across 3 branches:
- **Foundation**: DBMS Basics (`D01`), Relational Model (`D02`)
- **Design**: Keys (`D03`), Integrity Constraints (`D04`), Functional Dependencies (`D12`), Normalization (`D13`)
- **SQL**: SQL Basics (`D08`), SQL Joins (`D09`)

### Graph Structure & Edge Direction
All edges represent `prerequisite -> dependent`:
- `D01` -> `D02`
- `D02` -> `D03`, `D04`, `D08`
- `D03` -> `D04`, `D12`, `D13`
- `D08` -> `D09`
- `D12` -> `D13`

> [!NOTE]
> **D09 Simplification Notice:** In this MVP graph, `D09` (SQL Joins) depends directly on `D08` (SQL Basics). The full university DBMS curriculum prerequisite of Relational Algebra (`D07`) is deliberately excluded for MVP scoping. This demo graph is not a complete DBMS curriculum.

### Concept Importance
Concept importance is defined as `descendant_count / 7`:
- `D01`: 7/7 = 1.0000
- `D02`: 6/7 ≈ 0.8571
- `D03`: 3/7 ≈ 0.4286
- `D08`: 1/7 ≈ 0.1429
- `D12`: 1/7 ≈ 0.1429
- `D04`: 0/7 = 0.0000
- `D09`: 0/7 = 0.0000
- `D13`: 0/7 = 0.0000

---

## Quickstart

### 1. Environment Setup
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 2. Run Database Migrations
```bash
cd backend
alembic upgrade head
```

### 3. Seed Curriculum Data
```bash
cd backend
python -m app.db.seed
```
Optional flags:
- `--dry-run`: Validate curriculum content without writing to the database.
- `--data-dir PATH`: Specify an alternate directory for seed JSON files.

### 4. Run Development Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Health Check
```bash
curl http://localhost:8000/health
# or
curl http://localhost:8000/api/v1/health
```

### 6. Run Tests
```bash
cd backend
pytest -v --cov=app
```

---

## Administrator Bootstrap & Identity Workflow (v3.0 Phase 6)

### One-Time Initial Administrator CLI Bootstrap
To prevent privilege escalation and eliminate default credentials, there is **no public administrator registration endpoint**. The first administrator must be created via the secure CLI bootstrap command:

```bash
cd backend

# Option A: Via environment variables (recommended for automated deployments)
export ADMIN_EMAIL="admin@mindmesh.org"
export ADMIN_PASSWORD="ReplaceWithAStrongSecret123!"
export ADMIN_NAME="Lead Administrator"
python -m app.core.bootstrap_admin

# Option B: Via secure interactive prompt
python -m app.core.bootstrap_admin
```

#### Bootstrap Behavior & Guardrails
- **Strictly One-Time:** If any record exists in `administrator_accounts`, the command immediately aborts with `BootstrapError` and exit code 1.
- **Credential Security:** Never prints passwords or tokens to stdout/stderr. Password hashes use `bcrypt` with unique salts.
- **Recovery Expectations:** If initial administrator credentials are lost, access cannot be recovered via public endpoints. Administrators must be managed via direct database administrative procedures or dedicated identity provider integrations in production.

---

## Identity & Authorization Model

### Roles & Endpoint Permissions
| Role | Capabilities | Protected Endpoints |
|---|---|---|
| **Student** | Access own assessment sessions, diagnostic graph, feedback, hints, learning completion, and epoch report. Cannot access educator or admin endpoints. | `/api/v1/sessions/*`, `/api/v1/students/me/*` |
| **Educator** | Self-registers in `pending` state. Once approved by an administrator, can view assigned classes and assigned student records. Immediate 403 on suspension. | `/api/v1/educators/register`, `/api/v1/educators/me`, `/api/v1/educators/me/assignments` |
| **Administrator** | Created via CLI bootstrap. Can review pending educators, approve, suspend, and assign educators to classes/sections. Logs immutable audit events. | `/api/v1/admin/educators*` |

### Assigned-Scope Authorization & Immediate Revocation
- **Class-Wide Grant:** An assignment with `section_id = null` grants access to all sections in that class.
- **Section-Specific Grant:** An assignment with a specific `section_id` restricts access strictly to that section. Cross-section access fails closed with `403 Forbidden`.
- **Immediate Revocation:** Authorization checks query the live database state on every request. If an educator is suspended or an assignment is revoked, the very next request fails immediately, even with a previously valid token.
