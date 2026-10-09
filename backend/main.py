"""
FastAPI service exposing MindMesh NetworkX Concept Graph Engine
"""

from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from pathlib import Path

from schemas import (
    ConceptSchema,
    QuestionSchema,
    DiagnosisRequest,
    DiagnosisResponse,
    RoadmapRequest,
    RoadmapResponse,
    GraphDataResponse,
    GraphNode,
    GraphEdge
)
from graph_engine import ConceptGraphEngine

app = FastAPI(
    title="Mind Mesh Adaptive Graph Engine API",
    description="NetworkX-powered prerequisite graph validation, Bayesian diagnostic updates, and root-gap isolation for DBMS.",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize NetworkX graph engine
engine = ConceptGraphEngine()

@app.get("/")
def read_root():
    return {
        "service": "Mind Mesh Graph Engine",
        "status": "online",
        "library": "NetworkX",
        "nodes": len(engine.G.nodes),
        "edges": len(engine.G.edges),
        "is_dag": True
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok", "networkx_version": "3.x"}

@app.get("/api/concepts", response_model=List[Dict[str, Any]])
def get_concepts():
    """Return all 18 DBMS concepts."""
    return list(engine.concepts_data.values())

@app.get("/api/questions", response_model=List[Dict[str, Any]])
def get_questions():
    """Return all 36 diagnostic question bank items."""
    return list(engine.questions_data.values())

@app.get("/api/graph", response_model=GraphDataResponse)
def get_graph_data():
    """
    FR-G1 & FR-G6: Return NetworkX graph nodes, directed edges, 
    transitive reduction edges, and topological order.
    """
    nodes: List[GraphNode] = []
    total_nodes = len(engine.G.nodes)

    for nid in engine.G.nodes():
        node_data = engine.concepts_data.get(nid, {})
        nodes.append(
            GraphNode(
                id=nid,
                name=node_data.get("name", nid),
                difficulty=node_data.get("difficulty", 1),
                tier=node_data.get("tier", 1),
                in_degree=engine.G.in_degree(nid),
                out_degree=engine.G.out_degree(nid),
                ancestor_count=len(engine.get_ancestors_with_distance(nid)),
                descendant_count=len(engine.get_dependents(nid)),
                importance=round(engine.compute_importance(nid), 3)
            )
        )

    edges = [GraphEdge(source=u, target=v) for u, v in engine.G.edges()]
    tr_edges = [GraphEdge(source=u, target=v) for u, v in engine.get_transitive_reduction()]
    topological_order = engine.get_topological_sort()

    return GraphDataResponse(
        nodes=nodes,
        edges=edges,
        transitive_reduced_edges=tr_edges,
        topological_order=topological_order,
        is_valid_dag=True
    )

@app.post("/api/diagnose", response_model=DiagnosisResponse)
def diagnose_student_quiz(payload: DiagnosisRequest):
    """
    FR-D6, FR-M1, FR-M2 & SRS Section 5.4:
    Process student quiz responses, apply Bayesian mastery updates,
    and trace root prerequisite gap using NetworkX shortest paths and blocker scores.
    """
    responses = [r.dict() for r in payload.responses]
    diagnosis = engine.diagnose_root_gap(responses)
    return diagnosis

@app.post("/api/roadmap", response_model=RoadmapResponse)
def generate_remediation_roadmap(payload: RoadmapRequest):
    """
    FR-G4: Topologically sorted learning path for remediating gaps.
    """
    steps = engine.generate_learning_roadmap(payload.gap_ids)
    ordered_ids = [s["concept_id"] for s in steps]
    return RoadmapResponse(
        ordered_concept_ids=ordered_ids,
        steps=steps
    )

if __name__ == "__main__":
    import uvicorn  # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
