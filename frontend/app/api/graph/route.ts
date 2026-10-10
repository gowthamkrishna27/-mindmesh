import { NextResponse } from 'next/server';
import { getConceptsFromDB, saveKnowledgeGraphToDB } from '@/lib/supabase';
import { ConceptGraphEngine } from '@/lib/graphEngine';

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;

export async function GET() {
  if (BACKEND_URL) {
    try {
      const res = await fetch(`${BACKEND_URL}/api/graph`, {
        signal: AbortSignal.timeout(12000),
        cache: 'no-store'
      });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data);
      }
    } catch {
      // Fallback smoothly to local engine
    }
  }

  const concepts = await getConceptsFromDB();
  const engine = new ConceptGraphEngine(concepts);
  return NextResponse.json(engine.getGraphData());
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const concepts = body.concepts || (Array.isArray(body) ? body : null);
    if (!concepts || !Array.isArray(concepts)) {
      return NextResponse.json({ error: 'Missing or invalid concepts array' }, { status: 400 });
    }
    const success = await saveKnowledgeGraphToDB(concepts);
    if (!success) {
      return NextResponse.json({ error: 'Failed to persist knowledge graph to database' }, { status: 500 });
    }
    const updatedConcepts = await getConceptsFromDB();
    const engine = new ConceptGraphEngine(updatedConcepts);
    return NextResponse.json({ success: true, count: updatedConcepts.length, graph: engine.getGraphData() });
  } catch (err: any) {
    return NextResponse.json({ error: err.message || 'Server error' }, { status: 500 });
  }
}

