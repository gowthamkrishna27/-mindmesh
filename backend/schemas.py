from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field  # type: ignore

class ResourceItem(BaseModel):
    title: str
    url: str
    summary: str

class ConceptSchema(BaseModel):
    id: str
    name: str
    description: str
    difficulty: int
    learning_objectives: List[str] = []
    prerequisites: List[str] = []
    resources: List[ResourceItem] = []
    x: Optional[float] = 0
    y: Optional[float] = 0
    tier: Optional[int] = 1

class QuestionOptionSchema(BaseModel):
    id: str
    text: str
    correct: bool
    maps_to: Optional[str] = None
    misconception: Optional[str] = None

class QuestionSchema(BaseModel):
    id: str
    concept: str
    family: Literal["A", "B"]
    difficulty: int
    prompt: str
    options: List[QuestionOptionSchema]
    explanation: str
    validation_status: Literal["draft", "reviewed"] = "reviewed"

class QuizAnswerSubmission(BaseModel):
    question_id: str
    concept_id: str
    option_id: str
    confidence: Literal["low", "medium", "high"] = "medium"
    response_ms: int = 1500

class StudentMasterySchema(BaseModel):
    concept_id: str
    p: float = Field(..., ge=0.0, le=1.0)
    n_direct: int = 0
    n_indirect: int = 0
    status: Literal["insufficient", "suspected", "confirmed", "rejected", "mastered"]
    blocker_score: Optional[float] = None
    uncertainty: Optional[float] = None

class DiagnosisRequest(BaseModel):
    student_id: Optional[str] = "demo-student"
    responses: List[QuizAnswerSubmission]

class DiagnosisResponse(BaseModel):
    target_failed_concept: Optional[str]
    root_gap_id: Optional[str]
    root_gap_name: Optional[str]
    evidence_path: List[str]
    mastery_map: Dict[str, StudentMasterySchema]
    confirmed_gaps: List[str]
    suspected_gaps: List[str]
    mastered: List[str]
    explanation: str

class RoadmapRequest(BaseModel):
    gap_ids: List[str]

class RoadmapStep(BaseModel):
    position: int
    concept_id: str
    concept_name: str
    prerequisites: List[str]
    rationale: str
    estimated_mins: int
    resources: List[ResourceItem]

class RoadmapResponse(BaseModel):
    ordered_concept_ids: List[str]
    steps: List[RoadmapStep]

class GraphNode(BaseModel):
    id: str
    name: str
    difficulty: int
    tier: int
    in_degree: int
    out_degree: int
    ancestor_count: int
    descendant_count: int
    importance: float

class GraphEdge(BaseModel):
    source: str
    target: str

class GraphDataResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    transitive_reduced_edges: List[GraphEdge]
    topological_order: List[str]
    is_valid_dag: bool
