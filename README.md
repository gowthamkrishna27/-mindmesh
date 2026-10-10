# MIND MESH: Adaptive Learning Dependency Graph

> **AI-VERSE Problem Statement 30: Adaptive Learning Dependency Graph**  
> Identifies knowledge gaps underneath what students learn, diagnoses root prerequisite blockers using Directed Acyclic Graphs (DAG), and generates personalized topological learning paths.

---

## ⚡ Quick Start Commands

### 1. Run Frontend (Next.js)

```powershell
cd frontend
npm install
npm run dev
```

The web application runs on: **[http://localhost:3000](http://localhost:3000)**

---

### 2. Run Backend (NetworkX + FastAPI)

```powershell
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- API Docs (Swagger): **[http://localhost:8000/docs](http://localhost:8000/docs)**
- Health Check: **[http://localhost:8000/api/health](http://localhost:8000/api/health)**

---

### 3. Run Backend Graph Unit Tests

To test DAG acyclicity validation, topological sorting, Bayesian mastery updates, and root-gap isolation:

```powershell
cd backend
python test_graph_engine.py
```

---

## 🔑 Demo Login Credentials

The application provides quick credentials on the login screen:

| Role | Email | Password |
|---|---|---|
| **Student** | `alex.chen@mindmesh.edu` | `student123` |
| **Educator** | `aris.thorne@mindmesh.edu` | `faculty123` |

---

## 🐳 Run with Docker (Backend)

```bash
cd backend
docker build -t mindmesh-backend .
docker run -p 8000:8000 mindmesh-backend
```

---

## 📋 Full Command Reference

### Frontend Commands (`/frontend`)
| Command | Action |
|---|---|
| `npm run dev` | Start Next.js development server with hot-reloading at `localhost:3000` |
| `npm run build` | Build optimized production bundle |
| `npm run start` | Serve compiled production build |

### Backend Commands (`/backend`)
| Command | Action |
|---|---|
| `uvicorn main:app --reload --port 8000` | Start FastAPI service with hot-reloading |
| `python test_graph_engine.py` | Run NetworkX requirement test suite (FR-G1 to FR-G6) |
| `pip install -r requirements.txt` | Install Python dependencies (`fastapi`, `networkx`, `pydantic`, `uvicorn`) |

---

## 🛠️ Architecture

- **Frontend**: Next.js 16 (App Router), React 19, Tailwind CSS v4, Lucide Icons.
- **Backend & Graph Engine**: Python, NetworkX (`nx.DiGraph`), FastAPI, Pydantic.
- **Dataset**: 18 DBMS concepts, 36 multi-choice questions with distractor misconception mappings, and a 24-student simulated cohort benchmark.
