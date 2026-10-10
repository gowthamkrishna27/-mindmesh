const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

const conceptsData = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../data/concepts.json'), 'utf8')
);
const questionsData = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../data/questions.json'), 'utf8')
);

const cohortData = [
  { concept_id: "D01", name: "DBMS Basics", confirmed_gaps: 0, suspected_gaps: 2, mastered: 24, insufficient: 2, gap_rate: 7 },
  { concept_id: "D02", name: "Relational Model", confirmed_gaps: 1, suspected_gaps: 3, mastered: 22, insufficient: 2, gap_rate: 14 },
  { concept_id: "D03", name: "Keys", confirmed_gaps: 5, suspected_gaps: 7, mastered: 14, insufficient: 2, gap_rate: 43 },
  { concept_id: "D04", name: "Integrity Constraints", confirmed_gaps: 2, suspected_gaps: 4, mastered: 18, insufficient: 4, gap_rate: 21 },
  { concept_id: "D05", name: "ER Modeling", confirmed_gaps: 1, suspected_gaps: 2, mastered: 23, insufficient: 2, gap_rate: 11 },
  { concept_id: "D06", name: "ER-to-Relational Mapping", confirmed_gaps: 4, suspected_gaps: 6, mastered: 15, insufficient: 3, gap_rate: 36 },
  { concept_id: "D07", name: "Relational Algebra", confirmed_gaps: 3, suspected_gaps: 5, mastered: 18, insufficient: 2, gap_rate: 29 },
  { concept_id: "D08", name: "SQL Basics", confirmed_gaps: 1, suspected_gaps: 2, mastered: 25, insufficient: 0, gap_rate: 11 },
  { concept_id: "D09", name: "SQL Joins", confirmed_gaps: 4, suspected_gaps: 6, mastered: 16, insufficient: 2, gap_rate: 36 },
  { concept_id: "D10", name: "Aggregation & GROUP BY", confirmed_gaps: 2, suspected_gaps: 5, mastered: 19, insufficient: 2, gap_rate: 25 },
  { concept_id: "D11", name: "Subqueries & Views", confirmed_gaps: 6, suspected_gaps: 8, mastered: 11, insufficient: 3, gap_rate: 50 },
  { concept_id: "D12", name: "Functional Dependencies", confirmed_gaps: 11, suspected_gaps: 7, mastered: 8, insufficient: 2, gap_rate: 64 },
  { concept_id: "D13", name: "Normalization (1NF-3NF)", confirmed_gaps: 9, suspected_gaps: 8, mastered: 9, insufficient: 2, gap_rate: 61 },
  { concept_id: "D14", name: "BCNF & Decomposition", confirmed_gaps: 8, suspected_gaps: 6, mastered: 10, insufficient: 4, gap_rate: 50 },
  { concept_id: "D15", name: "Transactions & ACID", confirmed_gaps: 2, suspected_gaps: 4, mastered: 20, insufficient: 2, gap_rate: 21 },
  { concept_id: "D16", name: "Concurrency Control", confirmed_gaps: 7, suspected_gaps: 6, mastered: 12, insufficient: 3, gap_rate: 46 },
  { concept_id: "D17", name: "Indexing (B+ trees)", confirmed_gaps: 6, suspected_gaps: 7, mastered: 12, insufficient: 3, gap_rate: 46 },
  { concept_id: "D18", name: "Query Optimization", confirmed_gaps: 8, suspected_gaps: 9, mastered: 8, insufficient: 3, gap_rate: 61 }
];

const benchmarksData = [
  {
    strategy: "Baseline A: Fixed Curriculum Order",
    avg_questions_to_diagnose: 11.4,
    diagnostic_accuracy_pct: 54,
    time_efficiency_mins: 28.5,
    root_gap_discovery_rate: 48,
    color: "#94a3b8"
  },
  {
    strategy: "Baseline B: Lowest-Topic-First",
    avg_questions_to_diagnose: 8.7,
    diagnostic_accuracy_pct: 68,
    time_efficiency_mins: 22.0,
    root_gap_discovery_rate: 65,
    color: "#f59e0b"
  },
  {
    strategy: "MIND MESH: Prerequisite DAG Diagnosis",
    avg_questions_to_diagnose: 4.8,
    diagnostic_accuracy_pct: 94,
    time_efficiency_mins: 11.2,
    root_gap_discovery_rate: 96,
    color: "#10b981"
  }
];

async function setupTables() {
  const client = new Client({
    host: 'db.aquuguxootxwytaxsxhd.supabase.co',
    port: 5432,
    user: 'postgres',
    password: 'nkZOVCl7BE24oxtc',
    database: 'postgres',
    ssl: { rejectUnauthorized: false }
  });

  console.log('Connecting to Supabase PostgreSQL...');
  await client.connect();
  console.log('Connected!');

  try {
    await client.query('BEGIN;');

    console.log('1. Creating Tables...');
    await client.query(`
      -- Users Table
      CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(64) PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        role VARCHAR(32) NOT NULL CHECK (role IN ('student', 'educator')),
        created_at TIMESTAMPTZ DEFAULT NOW()
      );

      -- Concepts Table
      CREATE TABLE IF NOT EXISTS concepts (
        id VARCHAR(16) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        difficulty SMALLINT NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
        tier SMALLINT DEFAULT 1,
        x INTEGER DEFAULT 0,
        y INTEGER DEFAULT 0,
        learning_objectives JSONB DEFAULT '[]'::jsonb,
        resources JSONB DEFAULT '[]'::jsonb,
        created_at TIMESTAMPTZ DEFAULT NOW()
      );

      -- Prerequisite Edges Table (Normalized Directed Acyclic Graph Edges)
      CREATE TABLE IF NOT EXISTS concept_prerequisites (
        source_id VARCHAR(16) REFERENCES concepts(id) ON DELETE CASCADE,
        target_id VARCHAR(16) REFERENCES concepts(id) ON DELETE CASCADE,
        PRIMARY KEY (source_id, target_id)
      );

      -- Questions Table
      CREATE TABLE IF NOT EXISTS questions (
        id VARCHAR(16) PRIMARY KEY,
        concept_id VARCHAR(16) NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
        family CHAR(1) NOT NULL CHECK (family IN ('A', 'B')),
        difficulty SMALLINT NOT NULL DEFAULT 1,
        prompt TEXT NOT NULL,
        options JSONB NOT NULL,
        explanation TEXT,
        validation_status VARCHAR(32) DEFAULT 'reviewed',
        created_at TIMESTAMPTZ DEFAULT NOW()
      );

      -- Student Concept Mastery Table
      CREATE TABLE IF NOT EXISTS student_mastery (
        id BIGSERIAL PRIMARY KEY,
        student_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        concept_id VARCHAR(16) NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
        p NUMERIC(4,2) NOT NULL DEFAULT 0.50,
        n_direct SMALLINT NOT NULL DEFAULT 0,
        n_indirect SMALLINT NOT NULL DEFAULT 0,
        status VARCHAR(32) NOT NULL CHECK (status IN ('mastered', 'confirmed', 'suspected', 'untested')),
        blocker_score NUMERIC(4,2) DEFAULT 0.00,
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        CONSTRAINT uq_student_concept UNIQUE (student_id, concept_id)
      );

      -- Quiz Responses Trail Table
      CREATE TABLE IF NOT EXISTS quiz_responses (
        id VARCHAR(64) PRIMARY KEY,
        student_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        question_id VARCHAR(16) NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
        concept_id VARCHAR(16) NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
        option_id CHAR(1) NOT NULL,
        correct BOOLEAN NOT NULL,
        confidence VARCHAR(16) NOT NULL CHECK (confidence IN ('low', 'medium', 'high')),
        response_ms INTEGER NOT NULL DEFAULT 0,
        evidence_weight NUMERIC(3,2) NOT NULL DEFAULT 1.00,
        distractor_mapped_to VARCHAR(16),
        misconception TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
      );

      -- Cohort Heatmap Metrics Table (For Educator Portal)
      CREATE TABLE IF NOT EXISTS cohort_heatmap (
        concept_id VARCHAR(16) PRIMARY KEY REFERENCES concepts(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        confirmed_gaps SMALLINT NOT NULL DEFAULT 0,
        suspected_gaps SMALLINT NOT NULL DEFAULT 0,
        mastered SMALLINT NOT NULL DEFAULT 0,
        insufficient SMALLINT NOT NULL DEFAULT 0,
        gap_rate NUMERIC(4,1) NOT NULL DEFAULT 0.0,
        updated_at TIMESTAMPTZ DEFAULT NOW()
      );

      -- Diagnostic Benchmarks Table
      CREATE TABLE IF NOT EXISTS benchmarks (
        id SERIAL PRIMARY KEY,
        strategy VARCHAR(255) NOT NULL,
        avg_questions_to_diagnose NUMERIC(4,1) NOT NULL,
        diagnostic_accuracy_pct SMALLINT NOT NULL,
        time_efficiency_mins NUMERIC(4,1) NOT NULL,
        root_gap_discovery_rate SMALLINT NOT NULL,
        color VARCHAR(32) NOT NULL
      );
    `);

    console.log('2. Creating Indexes for maximum query efficiency...');
    await client.query(`
      CREATE INDEX IF NOT EXISTS idx_questions_concept_family ON questions(concept_id, family);
      CREATE INDEX IF NOT EXISTS idx_prereq_target ON concept_prerequisites(target_id);
      CREATE INDEX IF NOT EXISTS idx_prereq_source ON concept_prerequisites(source_id);
      CREATE INDEX IF NOT EXISTS idx_mastery_student_status ON student_mastery(student_id, status);
      CREATE INDEX IF NOT EXISTS idx_responses_student ON quiz_responses(student_id, created_at DESC);
      CREATE INDEX IF NOT EXISTS idx_responses_concept ON quiz_responses(concept_id);
    `);

    console.log('3. Inserting Demo Users...');
    await client.query(`
      INSERT INTO users (id, email, name, role)
      VALUES 
        ('usr_alex_chen', 'alex.chen@mindmesh.edu', 'Alex Chen', 'student'),
        ('usr_aris_thorne', 'aris.thorne@mindmesh.edu', 'Dr. Aris Thorne', 'educator')
      ON CONFLICT (id) DO UPDATE 
        SET email = EXCLUDED.email, name = EXCLUDED.name, role = EXCLUDED.role;
    `);

    console.log('4. Inserting Concepts...');
    for (const c of conceptsData) {
      await client.query(`
        INSERT INTO concepts (id, name, description, difficulty, tier, x, y, learning_objectives, resources)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (id) DO UPDATE SET
          name = EXCLUDED.name,
          description = EXCLUDED.description,
          difficulty = EXCLUDED.difficulty,
          tier = EXCLUDED.tier,
          x = EXCLUDED.x,
          y = EXCLUDED.y,
          learning_objectives = EXCLUDED.learning_objectives,
          resources = EXCLUDED.resources;
      `, [
        c.id,
        c.name,
        c.description,
        c.difficulty,
        c.tier || 1,
        c.x || 0,
        c.y || 0,
        JSON.stringify(c.learning_objectives || []),
        JSON.stringify(c.resources || [])
      ]);
    }

    console.log('5. Inserting Prerequisite Edges...');
    for (const c of conceptsData) {
      if (Array.isArray(c.prerequisites)) {
        for (const prereqId of c.prerequisites) {
          await client.query(`
            INSERT INTO concept_prerequisites (source_id, target_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING;
          `, [prereqId, c.id]);
        }
      }
    }

    console.log('6. Inserting Questions...');
    for (const q of questionsData) {
      await client.query(`
        INSERT INTO questions (id, concept_id, family, difficulty, prompt, options, explanation, validation_status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (id) DO UPDATE SET
          concept_id = EXCLUDED.concept_id,
          family = EXCLUDED.family,
          difficulty = EXCLUDED.difficulty,
          prompt = EXCLUDED.prompt,
          options = EXCLUDED.options,
          explanation = EXCLUDED.explanation,
          validation_status = EXCLUDED.validation_status;
      `, [
        q.id,
        q.concept,
        q.family,
        q.difficulty,
        q.prompt,
        JSON.stringify(q.options),
        q.explanation || '',
        q.validation_status || 'reviewed'
      ]);
    }

    console.log('7. Inserting Cohort Heatmap Data...');
    for (const ch of cohortData) {
      await client.query(`
        INSERT INTO cohort_heatmap (concept_id, name, confirmed_gaps, suspected_gaps, mastered, insufficient, gap_rate)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (concept_id) DO UPDATE SET
          name = EXCLUDED.name,
          confirmed_gaps = EXCLUDED.confirmed_gaps,
          suspected_gaps = EXCLUDED.suspected_gaps,
          mastered = EXCLUDED.mastered,
          insufficient = EXCLUDED.insufficient,
          gap_rate = EXCLUDED.gap_rate;
      `, [ch.concept_id, ch.name, ch.confirmed_gaps, ch.suspected_gaps, ch.mastered, ch.insufficient, ch.gap_rate]);
    }

    console.log('8. Inserting Benchmarks Data...');
    await client.query('DELETE FROM benchmarks;');
    for (const b of benchmarksData) {
      await client.query(`
        INSERT INTO benchmarks (strategy, avg_questions_to_diagnose, diagnostic_accuracy_pct, time_efficiency_mins, root_gap_discovery_rate, color)
        VALUES ($1, $2, $3, $4, $5, $6);
      `, [b.strategy, b.avg_questions_to_diagnose, b.diagnostic_accuracy_pct, b.time_efficiency_mins, b.root_gap_discovery_rate, b.color]);
    }

    console.log('9. Inserting Initial Alex Chen Mastery Profile...');
    const initialMasteries = [
      { cid: 'D01', p: 0.92, nd: 3, ni: 0, st: 'mastered', bl: 0.0 },
      { cid: 'D02', p: 0.88, nd: 2, ni: 0, st: 'mastered', bl: 0.0 },
      { cid: 'D03', p: 0.74, nd: 2, ni: 1, st: 'mastered', bl: 0.0 },
      { cid: 'D08', p: 0.85, nd: 2, ni: 0, st: 'mastered', bl: 0.0 },
      { cid: 'D12', p: 0.18, nd: 2, ni: 2, st: 'confirmed', bl: 0.52 },
      { cid: 'D13', p: 0.22, nd: 2, ni: 0, st: 'confirmed', bl: 0.47 }
    ];
    for (const m of initialMasteries) {
      await client.query(`
        INSERT INTO student_mastery (student_id, concept_id, p, n_direct, n_indirect, status, blocker_score)
        VALUES ('usr_alex_chen', $1, $2, $3, $4, $5, $6)
        ON CONFLICT (student_id, concept_id) DO UPDATE SET
          p = EXCLUDED.p,
          n_direct = EXCLUDED.n_direct,
          n_indirect = EXCLUDED.n_indirect,
          status = EXCLUDED.status,
          blocker_score = EXCLUDED.blocker_score;
      `, [m.cid, m.p, m.nd, m.ni, m.st, m.bl]);
    }

    console.log('10. Configuring Row Level Security (RLS) and Grants for Supabase Client...');
    await client.query(`
      ALTER TABLE users ENABLE ROW LEVEL SECURITY;
      ALTER TABLE concepts ENABLE ROW LEVEL SECURITY;
      ALTER TABLE concept_prerequisites ENABLE ROW LEVEL SECURITY;
      ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
      ALTER TABLE student_mastery ENABLE ROW LEVEL SECURITY;
      ALTER TABLE quiz_responses ENABLE ROW LEVEL SECURITY;
      ALTER TABLE cohort_heatmap ENABLE ROW LEVEL SECURITY;
      ALTER TABLE benchmarks ENABLE ROW LEVEL SECURITY;

      DROP POLICY IF EXISTS "Public read concepts" ON concepts;
      CREATE POLICY "Public read concepts" ON concepts FOR SELECT USING (true);

      DROP POLICY IF EXISTS "Public read prerequisites" ON concept_prerequisites;
      CREATE POLICY "Public read prerequisites" ON concept_prerequisites FOR SELECT USING (true);

      DROP POLICY IF EXISTS "Public read questions" ON questions;
      CREATE POLICY "Public read questions" ON questions FOR SELECT USING (true);

      DROP POLICY IF EXISTS "Public read cohort" ON cohort_heatmap;
      CREATE POLICY "Public read cohort" ON cohort_heatmap FOR SELECT USING (true);

      DROP POLICY IF EXISTS "Public read benchmarks" ON benchmarks;
      CREATE POLICY "Public read benchmarks" ON benchmarks FOR SELECT USING (true);

      DROP POLICY IF EXISTS "Public read users" ON users;
      CREATE POLICY "Public read users" ON users FOR SELECT USING (true);

      DROP POLICY IF EXISTS "Public read mastery" ON student_mastery;
      CREATE POLICY "Public read mastery" ON student_mastery FOR SELECT USING (true);

      DROP POLICY IF EXISTS "Public read responses" ON quiz_responses;
      CREATE POLICY "Public read responses" ON quiz_responses FOR SELECT USING (true);

      DROP POLICY IF EXISTS "Public insert responses" ON quiz_responses;
      CREATE POLICY "Public insert responses" ON quiz_responses FOR INSERT WITH CHECK (true);

      DROP POLICY IF EXISTS "Public manage mastery" ON student_mastery;
      CREATE POLICY "Public manage mastery" ON student_mastery FOR ALL USING (true);

      GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;
      GRANT INSERT, UPDATE, DELETE ON student_mastery, quiz_responses, users TO anon, authenticated;
      GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
    `);

    await client.query('COMMIT;');
    console.log('Transaction committed successfully!');

    // Row Count Verifications
    console.log('\n--- VERIFYING TABLE ROW COUNTS ---');
    const tables = [
      'users',
      'concepts',
      'concept_prerequisites',
      'questions',
      'student_mastery',
      'cohort_heatmap',
      'benchmarks'
    ];
    for (const t of tables) {
      const res = await client.query(`SELECT COUNT(*) FROM ${t}`);
      console.log(`Table '${t}': ${res.rows[0].count} rows`);
    }

  } catch (err) {
    await client.query('ROLLBACK;');
    console.error('Error during setup:', err);
  } finally {
    await client.end();
  }
}

setupTables();
