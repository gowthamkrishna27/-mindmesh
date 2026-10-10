import { NextResponse } from 'next/server';
import { getConceptsFromDB } from '@/lib/supabase';

export async function GET() {
  try {
    const concepts = await getConceptsFromDB();
    if (!concepts || concepts.length === 0) {
      return NextResponse.json({ error: 'Failed to fetch concepts from database' }, { status: 500 });
    }
    return NextResponse.json(concepts);
  } catch (err: any) {
    return NextResponse.json({ error: err.message || 'Database error' }, { status: 500 });
  }
}
