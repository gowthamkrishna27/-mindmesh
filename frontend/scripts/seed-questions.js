const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

async function seedQuestions() {
  const questionsFilePath = path.join(__dirname, '../../backend/data/questions.json');
  console.log(`Reading questions from: ${questionsFilePath}`);

  if (!fs.existsSync(questionsFilePath)) {
    console.error(`File not found: ${questionsFilePath}`);
    process.exit(1);
  }

  const raw = fs.readFileSync(questionsFilePath, 'utf8');
  const questions = JSON.parse(raw);
  console.log(`Found ${questions.length} questions to seed.`);

  const client = new Client({
    host: 'db.aquuguxootxwytaxsxhd.supabase.co',
    port: 5432,
    user: 'postgres',
    password: 'nkZOVCl7BE24oxtc',
    database: 'postgres',
    ssl: { rejectUnauthorized: false }
  });

  try {
    await client.connect();
    console.log('Connected to Supabase PostgreSQL database.');

    await client.query('BEGIN;');

    let seededCount = 0;
    for (const q of questions) {
      const conceptId = q.concept || q.concept_id;
      const prompt = q.prompt;
      const family = q.family;
      const difficulty = q.difficulty || 1;
      const options = JSON.stringify(q.options || []);
      const explanation = q.explanation || '';
      const validationStatus = q.validation_status || 'reviewed';

      await client.query(
        `INSERT INTO questions (id, concept_id, family, difficulty, prompt, options, explanation, validation_status)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
         ON CONFLICT (id) DO UPDATE SET
           concept_id = EXCLUDED.concept_id,
           family = EXCLUDED.family,
           difficulty = EXCLUDED.difficulty,
           prompt = EXCLUDED.prompt,
           options = EXCLUDED.options,
           explanation = EXCLUDED.explanation,
           validation_status = EXCLUDED.validation_status;`,
        [q.id, conceptId, family, difficulty, prompt, options, explanation, validationStatus]
      );
      seededCount++;
    }

    await client.query('COMMIT;');
    console.log(`Successfully seeded/updated ${seededCount} questions in Supabase!`);

    // Verify row count
    const res = await client.query('SELECT COUNT(*) FROM questions;');
    console.log(`Total questions now in database: ${res.rows[0].count}`);

  } catch (err) {
    await client.query('ROLLBACK;').catch(() => {});
    console.error('Error seeding questions:', err);
  } finally {
    await client.end();
  }
}

seedQuestions();
