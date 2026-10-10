const { Client } = require('pg');

async function fixConstraints() {
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

    console.log('1. Updating student_mastery status check constraint...');
    await client.query(`
      ALTER TABLE student_mastery DROP CONSTRAINT IF EXISTS student_mastery_status_check;
      ALTER TABLE student_mastery ADD CONSTRAINT student_mastery_status_check 
        CHECK (status IN ('mastered', 'confirmed', 'suspected', 'insufficient', 'untested', 'rejected', 'uncertain'));
    `);

    console.log('2. Ensuring blocker_score can accept precision decimals...');
    await client.query(`
      ALTER TABLE student_mastery ALTER COLUMN blocker_score TYPE NUMERIC;
    `);

    console.log('3. Ensuring users table has password column if not present...');
    await client.query(`
      ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR(255);
    `);

    console.log('4. Ensuring RLS policies allow anon & authenticated to manage concepts & prerequisites...');
    await client.query(`
      DROP POLICY IF EXISTS "Public manage concepts" ON concepts;
      CREATE POLICY "Public manage concepts" ON concepts FOR ALL USING (true);

      DROP POLICY IF EXISTS "Public manage prerequisites" ON concept_prerequisites;
      CREATE POLICY "Public manage prerequisites" ON concept_prerequisites FOR ALL USING (true);

      GRANT INSERT, UPDATE, DELETE ON concepts, concept_prerequisites TO anon, authenticated;
    `);

    await client.query('COMMIT;');
    console.log('Successfully applied database fixes!');
  } catch (err) {
    await client.query('ROLLBACK;');
    console.error('Failed to apply database fixes:', err);
  } finally {
    await client.end();
  }
}

fixConstraints();
