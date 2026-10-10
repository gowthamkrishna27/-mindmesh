import { createClient } from '@supabase/supabase-js';
import {
  Concept,
  Question,
  StudentMastery,
  ResponseRecord,
  CohortHeatmapRow,
  SimulationBenchmarkItem
} from './types';

const supabaseUrl =
  process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://aquuguxootxwytaxsxhd.supabase.co';

const supabaseKey =
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  'sb_publishable_JS6eTq5s5Gm3a5KLm9-Zfw_NIz0PDQt';

export const supabase = createClient(supabaseUrl, supabaseKey);

// ==========================================
// 1. Live Database Queries (Concepts & Graph)
// ==========================================

export async function getConceptsFromDB(): Promise<Concept[]> {
  const { data: concepts, error } = await supabase
    .from('concepts')
    .select('*')
    .order('tier', { ascending: true })
    .order('id', { ascending: true });

  if (error || !concepts) {
    console.error('Error fetching concepts from Supabase:', error);
    return [];
  }

  const { data: edges } = await supabase.from('concept_prerequisites').select('*');
  const prereqMap: Record<string, string[]> = {};
  edges?.forEach((e: any) => {
    if (!prereqMap[e.target_id]) prereqMap[e.target_id] = [];
    prereqMap[e.target_id].push(e.source_id);
  });

  return concepts.map((c: any) => ({
    id: c.id,
    name: c.name,
    description: c.description || '',
    difficulty: c.difficulty,
    tier: c.tier || 1,
    x: c.x || 0,
    y: c.y || 0,
    learning_objectives: c.learning_objectives || [],
    prerequisites: prereqMap[c.id] || [],
    resources: c.resources || []
  }));
}

// ==========================================
// 2. Live Database Queries (Questions)
// ==========================================

export async function getQuestionsFromDB(family?: 'A' | 'B'): Promise<Question[]> {
  let query = supabase.from('questions').select('*').order('id', { ascending: true });
  if (family) {
    query = query.eq('family', family.toUpperCase());
  }

  const { data, error } = await query;
  if (error || !data) {
    console.error('Error fetching questions from Supabase:', error);
    return [];
  }

  return data.map((q: any) => ({
    id: q.id,
    concept: q.concept_id,
    family: q.family,
    difficulty: q.difficulty,
    prompt: q.prompt,
    options: q.options,
    explanation: q.explanation || '',
    validation_status: q.validation_status || 'reviewed'
  }));
}

// ==========================================
// 3. Live Cohort & Benchmarks Data
// ==========================================

export async function getCohortFromDB(): Promise<{
  cohort: CohortHeatmapRow[];
  benchmarks: SimulationBenchmarkItem[];
}> {
  const [cohortRes, benchmarksRes] = await Promise.all([
    supabase.from('cohort_heatmap').select('*').order('concept_id', { ascending: true }),
    supabase.from('benchmarks').select('*').order('id', { ascending: true })
  ]);

  return {
    cohort: cohortRes.data || [],
    benchmarks: benchmarksRes.data || []
  };
}

// ==========================================
// 4. Live Student Mastery & Evidence Storage
// ==========================================

export async function getStudentMasteryFromDB(
  studentId: string = 'usr_alex_chen'
): Promise<Record<string, StudentMastery>> {
  const { data, error } = await supabase
    .from('student_mastery')
    .select('*')
    .eq('student_id', studentId);

  if (error || !data) {
    console.error('Error fetching student mastery from Supabase:', error);
    return {};
  }

  const map: Record<string, StudentMastery> = {};
  data.forEach((row: any) => {
    map[row.concept_id] = {
      concept_id: row.concept_id,
      p: parseFloat(row.p),
      n_direct: row.n_direct,
      n_indirect: row.n_indirect,
      status: row.status,
      blocker_score: row.blocker_score ? parseFloat(row.blocker_score) : undefined
    };
  });
  return map;
}

export async function ensureUserExists(studentId: string = 'usr_alex_chen') {
  try {
    const { data } = await supabase.from('users').select('id').eq('id', studentId).maybeSingle();
    if (!data) {
      await supabase.from('users').insert({
        id: studentId,
        email: `${studentId}@mindmesh.edu`,
        name: studentId.replace(/^usr_/, '').replace(/_/g, ' '),
        role: 'student'
      });
    }
  } catch (err) {
    console.warn('Notice ensuring user in database:', err);
  }
}

const VALID_MASTERY_STATUSES = new Set([
  'mastered',
  'confirmed',
  'suspected',
  'insufficient',
  'untested',
  'rejected',
  'uncertain'
]);

export async function saveStudentMasteryToDB(
  studentId: string = 'usr_alex_chen',
  masteryMap: Record<string, StudentMastery>
) {
  if (!masteryMap || Object.keys(masteryMap).length === 0) return;
  await ensureUserExists(studentId);

  const rows = Object.values(masteryMap).map(m => {
    const rawStatus = (m.status || '').toLowerCase();
    const status = VALID_MASTERY_STATUSES.has(rawStatus) ? rawStatus : 'insufficient';
    return {
      student_id: studentId,
      concept_id: m.concept_id,
      p: typeof m.p === 'number' ? Number(m.p.toFixed(2)) : 0.5,
      n_direct: typeof m.n_direct === 'number' ? m.n_direct : 0,
      n_indirect: typeof m.n_indirect === 'number' ? m.n_indirect : 0,
      status: status,
      blocker_score: typeof m.blocker_score === 'number' ? Number(m.blocker_score.toFixed(4)) : 0.0,
      updated_at: new Date().toISOString()
    };
  });

  const { error } = await supabase
    .from('student_mastery')
    .upsert(rows, { onConflict: 'student_id,concept_id' });

  if (error) {
    console.error('Error saving mastery to Supabase:', error);
  }
}

export async function saveQuizResponsesToDB(
  studentId: string = 'usr_alex_chen',
  responses: ResponseRecord[]
) {
  if (!responses || !Array.isArray(responses) || responses.length === 0) return;
  await ensureUserExists(studentId);

  try {
    const rows = responses.map(r => ({
      id: r.id || 'R_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6),
      student_id: String(studentId || 'usr_alex_chen'),
      question_id: String(r.question_id),
      concept_id: String(r.concept_id),
      option_id: String(r.option_id || 'a'),
      correct: Boolean(r.correct),
      confidence: (['low', 'medium', 'high'].includes(r.confidence) ? r.confidence : 'medium'),
      response_ms: Number(r.response_ms || 0),
      evidence_weight: Number(r.evidence_weight || 1.0),
      distractor_mapped_to: r.distractor_mapped_to || null,
      misconception: r.misconception || null,
      created_at: new Date().toISOString()
    }));

    const { error } = await supabase.from('quiz_responses').insert(rows);
    if (error) {
      console.warn('Notice saving quiz responses to Supabase:', error.message);
    }
  } catch (err) {
    console.warn('Quiz responses save bypassed:', err);
  }
}

export async function getQuizResponsesFromDB(studentId: string = 'usr_alex_chen'): Promise<ResponseRecord[]> {
  try {
    const { data, error } = await supabase
      .from('quiz_responses')
      .select('*')
      .eq('student_id', studentId)
      .order('created_at', { ascending: false })
      .limit(50);

    if (error || !data) return [];
    return data.map((r: any) => ({
      id: r.id,
      question_id: r.question_id,
      concept_id: r.concept_id,
      option_id: r.option_id,
      correct: Boolean(r.correct),
      confidence: r.confidence || 'medium',
      response_ms: Number(r.response_ms || 0),
      evidence_weight: Number(r.evidence_weight || 1.0),
      distractor_mapped_to: r.distractor_mapped_to || undefined,
      misconception: r.misconception || undefined,
      timestamp: r.created_at || new Date().toISOString()
    }));
  } catch (err) {
    console.warn('Failed to fetch quiz responses from DB:', err);
    return [];
  }
}

export async function saveKnowledgeGraphToDB(concepts: Concept[]): Promise<boolean> {
  if (!concepts || !Array.isArray(concepts) || concepts.length === 0) return false;
  try {
    // 1. Upsert concepts table
    const conceptRows = concepts.map(c => ({
      id: c.id,
      name: c.name,
      description: c.description || '',
      difficulty: c.difficulty || 1,
      tier: c.tier || 1,
      x: c.x || 0,
      y: c.y || 0,
      learning_objectives: c.learning_objectives || [],
      resources: c.resources || []
    }));

    const { error: conceptErr } = await supabase
      .from('concepts')
      .upsert(conceptRows, { onConflict: 'id' });

    if (conceptErr) {
      console.error('Error saving concepts to Supabase:', conceptErr);
      return false;
    }

    // 2. Upsert prerequisite edges
    const edgeRows: Array<{ source_id: string; target_id: string }> = [];
    concepts.forEach(c => {
      (c.prerequisites || []).forEach(prereqId => {
        edgeRows.push({ source_id: prereqId, target_id: c.id });
      });
    });

    if (edgeRows.length > 0) {
      const { error: edgeErr } = await supabase
        .from('concept_prerequisites')
        .upsert(edgeRows, { onConflict: 'source_id,target_id' });

      if (edgeErr) {
        console.error('Error saving prerequisite edges to Supabase:', edgeErr);
      }
    }
    return true;
  } catch (err) {
    console.error('Error in saveKnowledgeGraphToDB:', err);
    return false;
  }
}

// ==========================================
// 5. Live Authentication against Database
// ==========================================

export async function authenticateUserInDB(email: string, passwordAttempt: string) {
  const { data: user, error } = await supabase
    .from('users')
    .select('*')
    .eq('email', email.trim().toLowerCase())
    .single();

  if (error || !user) {
    return { success: false, error: 'Account not found. Please verify your email or sign up.' };
  }

  if (user.password && user.password !== passwordAttempt) {
    return { success: false, error: 'Incorrect password. Please verify your credentials.' };
  }

  return { success: true, user };
}

export async function registerUserInDB(params: {
  email: string;
  name: string;
  role: 'student' | 'educator';
  password: string;
}) {
  const { data: existing } = await supabase
    .from('users')
    .select('id')
    .eq('email', params.email.trim().toLowerCase())
    .maybeSingle();

  if (existing) {
    return { success: false, error: 'An account with this email address already exists.' };
  }

  const newId = 'usr_' + Date.now();
  const { data, error } = await supabase
    .from('users')
    .insert({
      id: newId,
      email: params.email.trim().toLowerCase(),
      name: params.name.trim(),
      role: params.role,
      password: params.password
    })
    .select()
    .single();

  if (error) {
    return { success: false, error: error.message };
  }

  // New students start with a clean slate until they take the diagnostic quiz
  return { success: true, user: data };
}
