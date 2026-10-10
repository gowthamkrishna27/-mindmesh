import { NextResponse } from 'next/server';
import { getCohortFromDB } from '@/lib/supabase';

export async function GET() {
  try {
    const { cohort, benchmarks } = await getCohortFromDB();

    return NextResponse.json({
      cohort,
      benchmarks,
      total_students: 24,
      subject: 'Database Management Systems (DBMS)'
    });
  } catch (err: any) {
    return NextResponse.json({ error: err.message || 'Database error' }, { status: 500 });
  }
}
