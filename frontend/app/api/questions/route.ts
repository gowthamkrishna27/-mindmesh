import { NextRequest, NextResponse } from 'next/server';
import { getQuestionsFromDB } from '@/lib/supabase';

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const familyParam = searchParams.get('family');
  const family = familyParam === 'A' || familyParam === 'B' ? familyParam : undefined;

  if (BACKEND_URL) {
    try {
      const res = await fetch(`${BACKEND_URL}/api/questions`, {
        signal: AbortSignal.timeout(12000),
        cache: 'no-store'
      });
      if (res.ok) {
        let questions: any[] = await res.json();
        if (family) {
          questions = questions.filter(q => (q.family || '').toUpperCase() === family);
        }
        return NextResponse.json(questions);
      }
    } catch {
      // Fallback silently to database
    }
  }

  try {
    const questions = await getQuestionsFromDB(family);
    return NextResponse.json(questions);
  } catch (err: any) {
    return NextResponse.json({ error: err.message || 'Error fetching questions' }, { status: 500 });
  }
}
