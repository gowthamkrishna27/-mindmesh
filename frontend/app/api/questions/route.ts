import { NextRequest, NextResponse } from 'next/server';
import { getQuestionsFromDB } from '@/lib/supabase';
import { Question } from '@/lib/types';
import fs from 'fs';
import path from 'path';

// Local bundled questions fallback ensuring 236 questions in all environments
function getLocalFallbackQuestions(): Question[] {
  try {
    const seedPath = path.join(process.cwd(), 'lib', 'seed-questions.json');
    if (fs.existsSync(seedPath)) {
      const data = JSON.parse(fs.readFileSync(seedPath, 'utf8'));
      return data;
    }
  } catch (err) {
    console.warn('Could not read seed-questions.json:', err);
  }
  return [];
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const familyParam = searchParams.get('family');
  const family = familyParam === 'A' || familyParam === 'B' ? familyParam : undefined;
  const conceptParam = searchParams.get('concept');
  const shuffleParam = searchParams.get('shuffle') === 'true';
  const limitParam = searchParams.get('limit') ? parseInt(searchParams.get('limit')!, 10) : undefined;
  const excludeParam = searchParams.get('exclude');
  const excludeIds = excludeParam ? new Set(excludeParam.split(',').map(s => s.trim())) : new Set();

  let questions: Question[] = [];

  // 1. Fetch live from Supabase PostgreSQL (source of truth, 236 questions)
  try {
    const dbQuestions = await getQuestionsFromDB(family);
    if (dbQuestions && dbQuestions.length > 0) {
      questions = dbQuestions;
    }
  } catch (err) {
    console.warn('Supabase fetch failed in /api/questions, falling back to local seed:', err);
  }

  // 2. If DB returned fewer than 50 questions or failed, supplement from local 236-question bank
  if (questions.length < 50) {
    const local = getLocalFallbackQuestions();
    if (local && local.length > 0) {
      let filtered = local;
      if (family) {
        filtered = filtered.filter(q => (q.family || '').toUpperCase() === family);
      }
      if (filtered.length > questions.length) {
        questions = filtered;
      }
    }
  }

  // 3. Filter by concept if requested
  if (conceptParam) {
    questions = questions.filter(q => q.concept === conceptParam);
  }

  // 4. Filter excluded IDs if requested
  if (excludeIds.size > 0) {
    questions = questions.filter(q => !excludeIds.has(q.id));
  }

  // 5. Shuffle if requested
  if (shuffleParam) {
    for (let i = questions.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [questions[i], questions[j]] = [questions[j], questions[i]];
    }
  }

  // 6. Apply limit if requested
  if (limitParam && limitParam > 0) {
    questions = questions.slice(0, limitParam);
  }

  return NextResponse.json(questions, {
    headers: {
      'Cache-Control': 'no-store, max-age=0'
    }
  });
}
