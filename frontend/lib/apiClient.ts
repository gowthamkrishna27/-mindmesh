import {
  Concept,
  Question,
  StudentMastery,
  ResponseRecord,
  LearningPathItem,
  CohortHeatmapRow,
  SimulationBenchmarkItem
} from './types';

// Points to Next.js API routes (which proxy or direct to NetworkX backend)
const API_BASE = '/api';

export interface BackendGraphNode {
  id: string;
  name: string;
  difficulty: number;
  tier: number;
  in_degree: number;
  out_degree: number;
  ancestor_count: number;
  descendant_count: number;
  importance: number;
}

export interface BackendGraphResponse {
  nodes: BackendGraphNode[];
  edges: Array<{ source: string; target: string }>;
  transitive_reduced_edges: Array<{ source: string; target: string }>;
  topological_order: string[];
  is_valid_dag: boolean;
}

export interface DiagnosisApiResponse {
  target_failed_concept?: string;
  root_gap_id?: string;
  root_gap_name?: string;
  evidence_path?: string[];
  mastery_map?: Record<string, StudentMastery>;
  confirmed_gaps?: string[];
  suspected_gaps?: string[];
  mastered?: string[];
  explanation?: string;
}

export async function fetchConcepts(): Promise<Concept[]> {
  try {
    const res = await fetch(`${API_BASE}/concepts`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch concepts:', err);
    return [];
  }
}

export async function fetchQuestions(
  family?: 'A' | 'B',
  options?: { concept?: string; shuffle?: boolean; limit?: number; exclude?: string[] }
): Promise<Question[]> {
  try {
    const params = new URLSearchParams();
    if (family) params.append('family', family);
    if (options?.concept) params.append('concept', options.concept);
    if (options?.shuffle) params.append('shuffle', 'true');
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.exclude && options.exclude.length > 0) {
      params.append('exclude', options.exclude.join(','));
    }

    const queryStr = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/questions${queryStr}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch questions:', err);
    return [];
  }
}

export async function fetchNetworkXGraph(): Promise<BackendGraphResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/graph`, { cache: 'no-store' });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch graph:', err);
    return null;
  }
}

export async function diagnoseWithNetworkX(
  responses: Array<{
    question_id: string;
    concept_id: string;
    option_id: string;
    confidence: 'low' | 'medium' | 'high';
    response_ms: number;
    correct?: boolean;
  }>,
  studentId?: string
): Promise<DiagnosisApiResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/diagnose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ responses, student_id: studentId }),
      cache: 'no-store'
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.error('Failed to diagnose with NetworkX:', err);
  }
  return null;
}

export async function fetchRoadmap(gapIds: string[] = ['D12', 'D13']): Promise<LearningPathItem[]> {
  try {
    const res = await fetch(`${API_BASE}/roadmap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gap_ids: gapIds }),
      cache: 'no-store'
    });
    if (res.ok) {
      const data = await res.json();
      return (data.steps || []).map((s: any, idx: number) => ({
        id: `PATH-${idx + 1}`,
        position: s.position || idx + 1,
        concept_id: s.concept_id,
        concept_name: s.concept_name,
        rationale: s.rationale,
        completed: false,
        estimated_mins: s.estimated_mins || 12,
        key_takeaways: [
          `Key foundation for ${s.concept_name}`,
          `Prerequisites: ${(s.prerequisites || []).join(', ') || 'None (Root Foundation)'}`
        ],
        practice_prompt: `Review and verify core rules for ${s.concept_name}.`,
        practice_solution: `Mastery verified for ${s.concept_name}.`,
        resources: s.resources || []
      }));
    }
  } catch (err) {
    console.error('Failed to fetch roadmap:', err);
  }
  return [];
}

export async function fetchCohortData(): Promise<{
  cohort: CohortHeatmapRow[];
  benchmarks: SimulationBenchmarkItem[];
}> {
  try {
    const res = await fetch(`${API_BASE}/cohort`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return {
      cohort: data.cohort || [],
      benchmarks: data.benchmarks || []
    };
  } catch (err) {
    console.error('Failed to fetch cohort data:', err);
    return { cohort: [], benchmarks: [] };
  }
}

export async function saveKnowledgeGraph(concepts: Concept[]): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/graph`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ concepts }),
      cache: 'no-store'
    });
    return res.ok;
  } catch (err) {
    console.error('Failed to save knowledge graph:', err);
    return false;
  }
}

export {
  getStudentMasteryFromDB as fetchStudentMastery,
  saveStudentMasteryToDB as saveStudentMastery,
  saveQuizResponsesToDB as saveQuizResponses,
  getQuizResponsesFromDB as fetchQuizResponses,
  saveKnowledgeGraphToDB
} from './supabase';
