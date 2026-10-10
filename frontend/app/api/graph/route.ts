import { NextResponse } from 'next/server';
import { getConceptsFromDB } from '@/lib/supabase';
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
