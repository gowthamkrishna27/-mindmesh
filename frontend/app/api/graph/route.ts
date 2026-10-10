import { NextResponse } from 'next/server';
import { getConceptsFromDB } from '@/lib/supabase';
import { ConceptGraphEngine } from '@/lib/graphEngine';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/graph`, {
      signal: AbortSignal.timeout(1000),
      cache: 'no-store'
    });
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch {
    // If Python backend not up, compute graph structure using native GraphEngine on live Supabase concepts
  }

  const concepts = await getConceptsFromDB();
  const engine = new ConceptGraphEngine(concepts);
  return NextResponse.json(engine.getGraphData());
}
