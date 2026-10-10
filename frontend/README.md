# MindMesh — Frontend

Modern Next.js 16 (App Router) + React 19 web application for the **MindMesh Adaptive Learning Dependency Graph**.

---

## ⚡ Quick Start

### 1. Install Dependencies
```powershell
npm install
```

### 2. Start Development Server
```powershell
npm run dev
```

App will run at: **[http://localhost:3000](http://localhost:3000)**

---

## 🔑 Demo Login Credentials

The application includes demo credentials:

| Role | Email | Password |
|---|---|---|
| **Student** | `alex.chen@mindmesh.edu` | `student123` |
| **Educator** | `aris.thorne@mindmesh.edu` | `faculty123` |

---

## 📋 Available Commands

| Command | Action |
|---|---|
| `npm run dev` | Starts local Next.js Turbopack development server on port `3000` |
| `npm run build` | Compiles and optimizes production bundle |
| `npm run start` | Serves compiled production build |

---

## 🔗 NetworkX Backend API Integration

The frontend connects directly to the Python **NetworkX FastAPI** service on `http://localhost:8000`:

1. In a separate terminal, launch the backend:
   ```powershell
   cd ..\backend
   .\venv\Scripts\Activate.ps1
   uvicorn main:app --reload --port 8000
   ```
2. Configure custom backend URL if needed in `.env.local`:
   ```env
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```
