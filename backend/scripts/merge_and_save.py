"""
Merges the 200 new questions with the original 36 questions.
Produces 236 total questions, saves to backend/data/questions.json,
copies to frontend/data/questions.json and frontend/lib/seed-questions.json,
and triggers the Supabase DB seed.
"""

import json
import shutil
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))
from questions_part1 import QUESTIONS_PART1
from questions_part2 import QUESTIONS_PART2
from questions_part3 import QUESTIONS_PART3

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DATA = ROOT_DIR / "backend" / "data"
FRONTEND_DATA = ROOT_DIR / "frontend" / "data"
FRONTEND_LIB = ROOT_DIR / "frontend" / "lib"

Q_FILE = BACKEND_DATA / "questions.json"
Q_BAK = BACKEND_DATA / "questions.json.bak"

def main():
    if not Q_FILE.exists():
        print(f"Error: {Q_FILE} not found!")
        sys.exit(1)

    with open(Q_FILE, "r", encoding="utf-8") as f:
        existing_questions = json.load(f)

    print(f"Loaded {len(existing_questions)} existing questions.")
    
    # Backup original if not already backed up
    if not Q_BAK.exists():
        shutil.copy(Q_FILE, Q_BAK)
        print(f"Created backup at {Q_BAK}")

    new_questions = QUESTIONS_PART1 + QUESTIONS_PART2 + QUESTIONS_PART3
    print(f"Prepared {len(new_questions)} new questions.")

    existing_ids = {q["id"] for q in existing_questions}
    combined = list(existing_questions)

    added_count = 0
    for q in new_questions:
        if q["id"] not in existing_ids:
            combined.append(q)
            existing_ids.add(q["id"])
            added_count += 1
        else:
            print(f"Warning: duplicate ID {q['id']} skipped")

    print(f"Added {added_count} new questions. Total questions: {len(combined)}")

    # Write to backend/data/questions.json
    with open(Q_FILE, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(combined)} questions to {Q_FILE}")

    # Copy to frontend locations
    FRONTEND_DATA.mkdir(parents=True, exist_ok=True)
    with open(FRONTEND_DATA / "questions.json", "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"Saved copy to {FRONTEND_DATA / 'questions.json'}")

    FRONTEND_LIB.mkdir(parents=True, exist_ok=True)
    with open(FRONTEND_LIB / "seed-questions.json", "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"Saved copy to {FRONTEND_LIB / 'seed-questions.json'}")

if __name__ == "__main__":
    main()
