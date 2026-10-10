const { createClient } = require('@supabase/supabase-js');
const url = 'https://aquuguxootxwytaxsxhd.supabase.co';
const key = 'sb_publishable_JS6eTq5s5Gm3a5KLm9-Zfw_NIz0PDQt';
const supabase = createClient(url, key);

async function runE2ETest() {
  console.log('--- 1. Testing User Account Persistence ---');
  const testStudentId = 'usr_gowtham_test';
  const { error: userErr } = await supabase.from('users').upsert({
    id: testStudentId,
    email: 'gowtham.test@mindmesh.edu',
    name: 'Gowtham Test',
    role: 'student'
  });
  console.log('User created/verified:', userErr ? userErr : 'SUCCESS');

  console.log('\n--- 2. Testing Account Progress / Mastery Map Persistence ---');
  const testMastery = {
    D01: {
      concept_id: 'D01',
      p: 0.95,
      n_direct: 3,
      n_indirect: 0,
      status: 'mastered',
      blocker_score: 0.0
    },
    D12: {
      concept_id: 'D12',
      p: 0.18,
      n_direct: 2,
      n_indirect: 1,
      status: 'confirmed',
      blocker_score: 0.8524
    },
    D13: {
      concept_id: 'D13',
      p: 0.32,
      n_direct: 1,
      n_indirect: 0,
      status: 'suspected',
      blocker_score: 0.6120
    },
    D04: {
      concept_id: 'D04',
      p: 0.50,
      n_direct: 0,
      n_indirect: 0,
      status: 'insufficient',
      blocker_score: 0.2500
    }
  };

  const masteryRows = Object.values(testMastery).map(m => ({
    student_id: testStudentId,
    concept_id: m.concept_id,
    p: m.p,
    n_direct: m.n_direct,
    n_indirect: m.n_indirect,
    status: m.status,
    blocker_score: m.blocker_score,
    updated_at: new Date().toISOString()
  }));

  const { error: masteryErr } = await supabase
    .from('student_mastery')
    .upsert(masteryRows, { onConflict: 'student_id,concept_id' });
  console.log('Mastery saved to DB:', masteryErr ? masteryErr : 'SUCCESS');

  const { data: fetchedMastery, error: fetchErr } = await supabase
    .from('student_mastery')
    .select('*')
    .eq('student_id', testStudentId);
  console.log('Fetched mastery rows count:', fetchedMastery ? fetchedMastery.length : 0);
  console.log('Statuses in DB:', fetchedMastery.map(r => `${r.concept_id}: ${r.status} (p=${r.p})`));

  console.log('\n--- 3. Testing Quiz Responses Persistence ---');
  const quizRow = {
    id: 'R_test_' + Date.now(),
    student_id: testStudentId,
    question_id: 'Q12A',
    concept_id: 'D12',
    option_id: 'c',
    correct: false,
    confidence: 'high',
    response_ms: 12500,
    evidence_weight: 1.25,
    distractor_mapped_to: 'D03',
    misconception: 'Confuses functional dependency constraint with row instance',
    created_at: new Date().toISOString()
  };
  const { error: respErr } = await supabase.from('quiz_responses').insert([quizRow]);
  console.log('Quiz response saved to DB:', respErr ? respErr : 'SUCCESS');

  console.log('\n--- 4. Testing Knowledge Graph DB Persistence ---');
  const { data: dbConcepts, error: cErr } = await supabase
    .from('concepts')
    .select('id, name, difficulty, tier')
    .order('id');
  const { data: dbPrereqs, error: pErr } = await supabase
    .from('concept_prerequisites')
    .select('source_id, target_id');

  console.log('Total concepts stored in DB:', dbConcepts ? dbConcepts.length : 0);
  console.log('Total prerequisite edges stored in DB:', dbPrereqs ? dbPrereqs.length : 0);

  // Clean up test data
  await supabase.from('quiz_responses').delete().eq('student_id', testStudentId);
  await supabase.from('student_mastery').delete().eq('student_id', testStudentId);
  await supabase.from('users').delete().eq('id', testStudentId);
  console.log('\n--- Test cleanup completed successfully! ---');
}

runE2ETest().catch(console.error);
