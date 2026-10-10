import { NextRequest, NextResponse } from 'next/server';
import { getConceptsFromDB, saveStudentMasteryToDB, saveQuizResponsesToDB } from '@/lib/supabase';
import { ConceptGraphEngine } from '@/lib/graphEngine';

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;

export async function POST(req: NextRequest) {
  let payload: any = { responses: [] };
  try {
    payload = await req.json();

    if (BACKEND_URL) {
      const res = await fetch(`${BACKEND_URL}/api/diagnose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(12000)
      });

      if (res.ok) {
        const data = await res.json();
        if (payload.student_id && data.mastery_map) {
          try {
            await saveStudentMasteryToDB(payload.student_id, data.mastery_map);
            if (Array.isArray(payload.responses) && payload.responses.length > 0) {
              await saveQuizResponsesToDB(payload.student_id, payload.responses);
            }
          } catch (dbErr) {
            console.error('Error saving diagnosis to database:', dbErr);
          }
        }
        return NextResponse.json(data);
      }
    }
  } catch {
    // Fallback smoothly to local graph engine
  }

  // Fallback to local ConceptGraphEngine
  const concepts = await getConceptsFromDB();
  const engine = new ConceptGraphEngine(concepts);
  const result = engine.diagnoseRootGap(payload.responses || []);

  if (payload.student_id && result.mastery_map) {
    try {
      await saveStudentMasteryToDB(payload.student_id, result.mastery_map);
      if (Array.isArray(payload.responses) && payload.responses.length > 0) {
        await saveQuizResponsesToDB(payload.student_id, payload.responses);
      }
    } catch (saveErr) {
      console.error('Error auto-saving diagnosis to database:', saveErr);
    }
  }

  return NextResponse.json(result);
}
