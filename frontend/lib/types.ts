export interface ConceptResource {
  title: string;
  url: string;
  summary: string;
}

export interface Concept {
  id: string;
  name: string;
  description: string;
  difficulty: number;
  learning_objectives: string[];
  prerequisites: string[];
  resources: ConceptResource[];
  x: number;
  y: number;
  tier: number;
}

export interface QuestionOption {
  id: string;
  text: string;
  correct: boolean;
  maps_to?: string;
  misconception?: string;
}

export interface Question {
  id: string;
  concept: string;
  family: 'A' | 'B';
  difficulty: number;
  prompt: string;
  options: QuestionOption[];
  explanation: string;
  validation_status: 'draft' | 'reviewed';
}

export interface StudentMastery {
  concept_id: string;
  p: number; // 0.02 - 0.98
  n_direct: number;
  n_indirect: number;
  status: 'insufficient' | 'suspected' | 'confirmed' | 'rejected' | 'mastered' | 'uncertain';
  blocker_score?: number;
  uncertainty?: number;
}

export interface ResponseRecord {
  id: string;
  question_id: string;
  concept_id: string;
  option_id: string;
  correct: boolean;
  confidence: 'low' | 'medium' | 'high';
  response_ms: number;
  evidence_weight: number;
  distractor_mapped_to?: string;
  misconception?: string;
  timestamp: string;
}

export interface LearningPathItem {
  id: string;
  position: number;
  concept_id: string;
  concept_name: string;
  rationale: string;
  completed: boolean;
  estimated_mins: number;
  key_takeaways: string[];
  practice_prompt: string;
  practice_solution: string;
  resources?: ConceptResource[];
}

export interface CohortHeatmapRow {
  concept_id: string;
  name: string;
  confirmed_gaps: number;
  suspected_gaps: number;
  mastered: number;
  insufficient: number;
  gap_rate: number;
}

export interface SimulationBenchmarkItem {
  strategy: string;
  avg_questions_to_diagnose: number;
  diagnostic_accuracy_pct: number;
  time_efficiency_mins: number;
  root_gap_discovery_rate: number;
  color: string;
}
