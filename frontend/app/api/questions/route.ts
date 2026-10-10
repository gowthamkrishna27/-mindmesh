import { NextRequest, NextResponse } from 'next/server';
import { getQuestionsFromDB } from '@/lib/supabase';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const familyParam = searchParams.get('family');
    const family = familyParam === 'A' || familyParam === 'B' ? familyParam : undefined;

    const questions = await getQuestionsFromDB(family);
    return NextResponse.json(questions);
  } catch (err: any) {
    return NextResponse.json({ error: err.message || 'Database error' }, { status: 500 });
  }
}
