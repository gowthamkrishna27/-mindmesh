import { Question } from './types';

/**
 * Fisher-Yates shuffle utility for arrays
 */
export function shuffleArray<T>(array: T[]): T[] {
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

const RECENT_KEY = 'mindmesh_recent_question_ids';
const MAX_RECENT_HISTORY = 120;

/**
 * Retrieve list of recently seen question IDs from localStorage
 */
export function getRecentQuestionIds(): string[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(RECENT_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

/**
 * Record question IDs as recently seen to avoid repeats in subsequent quizzes
 */
export function recordRecentQuestionIds(ids: string[]): void {
  if (typeof window === 'undefined' || !ids.length) return;
  try {
    const existing = getRecentQuestionIds();
    const combined = Array.from(new Set([...ids, ...existing])).slice(0, MAX_RECENT_HISTORY);
    localStorage.setItem(RECENT_KEY, JSON.stringify(combined));
  } catch {
    // Ignore storage errors
  }
}

/**
 * Clear recently seen questions history
 */
export function clearRecentQuestionHistory(): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.removeItem(RECENT_KEY);
  } catch {
    // Ignore storage errors
  }
}

export interface QuizSelectionOptions {
  /** Target count of questions for this quiz session (default: 8) */
  count?: number;
  /** Explicit question IDs to avoid */
  excludeIds?: string[];
  /** Whether to randomize the order of the 4 options inside each question (default: true) */
  shuffleOptions?: boolean;
  /** Restrict selection to specific concepts (e.g. ['D12', 'D13'] for retest) */
  conceptFilter?: string[];
}

/**
 * Efficient Stratified Adaptive Quiz Question Selector
 * - Shuffles available question pool
 * - Prioritizes fresh questions not recently answered by user
 * - Ensures coverage across distinct concepts and difficulty tiers
 * - Shuffles options order to prevent position memorization
 */
export function selectAdaptiveQuizQuestions(
  pool: Question[],
  options?: QuizSelectionOptions
): Question[] {
  if (!pool || pool.length === 0) return [];

  const count = options?.count ?? 8;
  const shuffleOpts = options?.shuffleOptions ?? true;
  const recentIds = new Set([
    ...(options?.excludeIds || []),
    ...getRecentQuestionIds()
  ]);

  // Apply concept filter if specified
  let candidates = options?.conceptFilter && options.conceptFilter.length > 0
    ? pool.filter(q => options.conceptFilter!.includes(q.concept))
    : [...pool];

  if (candidates.length === 0) candidates = [...pool];

  // Group questions by concept
  const conceptMap = new Map<string, Question[]>();
  candidates.forEach(q => {
    const list = conceptMap.get(q.concept) || [];
    list.push(q);
    conceptMap.set(q.concept, list);
  });

  // Collect unseen questions first for each concept
  const selected: Question[] = [];
  const conceptKeys = shuffleArray(Array.from(conceptMap.keys()));

  // Round 1: Select 1 unseen question per distinct concept
  for (const cId of conceptKeys) {
    if (selected.length >= count) break;
    const questionsForConcept = shuffleArray(conceptMap.get(cId) || []);
    // Try finding unseen question first
    const unseen = questionsForConcept.find(q => !recentIds.has(q.id));
    if (unseen) {
      selected.push(unseen);
    }
  }

  // Round 2: If we still need more questions, take unseen from any concept
  if (selected.length < count) {
    const alreadySelectedIds = new Set(selected.map(q => q.id));
    const remainingUnseen = shuffleArray(
      candidates.filter(q => !recentIds.has(q.id) && !alreadySelectedIds.has(q.id))
    );
    for (const q of remainingUnseen) {
      if (selected.length >= count) break;
      selected.push(q);
    }
  }

  // Round 3: If still not enough (e.g. user saw most of pool), recycle from seen questions
  if (selected.length < count) {
    const alreadySelectedIds = new Set(selected.map(q => q.id));
    const remainingSeen = shuffleArray(
      candidates.filter(q => !alreadySelectedIds.has(q.id))
    );
    for (const q of remainingSeen) {
      if (selected.length >= count) break;
      selected.push(q);
    }
  }

  // Final shuffle of question presentation order
  let finalQuestions = shuffleArray(selected);

  // Optionally shuffle options within each question
  if (shuffleOpts) {
    finalQuestions = finalQuestions.map(q => ({
      ...q,
      options: shuffleArray(q.options)
    }));
  }

  // Record selected IDs into history
  recordRecentQuestionIds(finalQuestions.map(q => q.id));

  return finalQuestions;
}
