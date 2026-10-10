import { NextRequest, NextResponse } from 'next/server';
import { getConceptsFromDB, saveKnowledgeGraphToDB } from '@/lib/supabase';

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

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const concepts = Array.isArray(body) ? body : (body.concepts || [body]);
    const success = await saveKnowledgeGraphToDB(concepts);
    if (!success) {
      return NextResponse.json({ error: 'Failed to save concepts to database' }, { status: 500 });
    }
    return NextResponse.json({ success: true, count: concepts.length });
  } catch (err: any) {
    return NextResponse.json({ error: err.message || 'Server error' }, { status: 500 });
  }
}

