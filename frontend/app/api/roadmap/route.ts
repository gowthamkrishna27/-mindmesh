import { NextRequest, NextResponse } from 'next/server';
import { getConceptsFromDB } from '@/lib/supabase';
import { ConceptGraphEngine } from '@/lib/graphEngine';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  let gap_ids: string[] = ['D12', 'D13'];
  try {
    const body = await req.json();
    if (body.gap_ids && Array.isArray(body.gap_ids) && body.gap_ids.length > 0) {
      gap_ids = body.gap_ids;
    }
  } catch {
    // defaults
  }

  try {
    const res = await fetch(`${BACKEND_URL}/api/roadmap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gap_ids }),
      signal: AbortSignal.timeout(1000)
    });
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch {
    // If backend offline, compute topological remediation sequence using ConceptGraphEngine
  }

  const concepts = await getConceptsFromDB();
  const engine = new ConceptGraphEngine(concepts);
  const steps = engine.generateLearningRoadmap(gap_ids);

  return NextResponse.json({
    ordered_concept_ids: steps.map(s => s.concept_id),
    steps
  });
}
