# Standardized Testing Plan for Family Office Agent

This document describes how to run **standardized tests** (e.g. AICPA-style multiple choice) against the agent **without a user profile**.

## API: `POST /test`

- **Purpose:** Send a single question and get a response using a fixed default profile. No profile creation or session management required.
- **Request body:** `{ "message": "Your question here" }`
- **Response:** Same as `POST /chat` (session_id, response, breakdown, evidence, modules_used, conversation_history). The session is temporary and discarded after the response.
- **Multiple-choice mode:** The backend automatically treats `/test` requests as multiple-choice. The agent is instructed to respond with **only** the letter of the correct answer (A, B, C, or D) so that automated scoring works. No memos or explanations are returned.

### Example (curl)

```bash
curl -s -X POST http://localhost:8000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "A taxpayer understated tax by $10,000. Total tax was $50,000. No disclosure; basis is reasonable. How much accuracy-related penalty? A. $0 B. $1,000 C. $2,000 D. $10,000"}' \
  | python3 -m json.tool
```

### Example (Python)

```python
import requests
r = requests.post("http://localhost:8000/test", json={"message": "What is the estate tax exemption in 2024?"})
print(r.json()["response"])
```

## Test runner script

Use the script to run many questions from a JSONL file and optionally check answers.

### 1. Question file format (JSONL)

One JSON object per line. Fields:

| Field       | Required | Description                                      |
|------------|----------|--------------------------------------------------|
| `question` | Yes      | Full question text (or use `text` / `message`)   |
| `id`       | No       | Question id for reporting (default: q1, q2, …)   |
| `expected`  | No       | Expected answer letter, e.g. `"A"` (for scoring) |

Example `scripts/data/sample_questions.jsonl`:

```jsonl
{"id": "q1", "question": "Your multiple choice question? A. opt1 B. opt2 C. opt3", "expected": "B"}
{"id": "q2", "question": "Another question?", "expected": null}
```

### 2. Run tests

Backend must be running (`cd backend && uvicorn app.main:app --reload`).

```bash
cd backend

# Default: run scripts/data/sample_questions.jsonl
python scripts/run_standardized_tests.py

# Custom question file
python scripts/run_standardized_tests.py path/to/my_questions.jsonl

# Verbose (print full Q&A)
python scripts/run_standardized_tests.py -v

# Write results to JSON
python scripts/run_standardized_tests.py -o results.json
```

### 3. Scoring

- If you include an `expected` field (e.g. `"A"`), the script tries to infer the agent’s chosen letter from the response and reports PASS/FAIL.
- Summary: `Score: X/Y (with expected answer)` at the end.

## Adding AICPA-style questions

1. Create or edit a JSONL file (e.g. `backend/scripts/data/aicpa_tax.jsonl`).
2. One line per question, e.g.:
   - `{"id": "T001", "question": "Full question text... A. ... B. ... C. ... D. ...", "expected": "C"}`
3. Run: `python scripts/run_standardized_tests.py scripts/data/aicpa_tax.jsonl -v -o aicpa_results.json`

**Included:** `scripts/data/aicpa_questions.jsonl` contains 78 parsed AICPA-style multiple choice questions (tax, filing status, penalties, etc.). To run them:

```bash
cd backend
python scripts/run_standardized_tests.py scripts/data/aicpa_questions.jsonl -v -o aicpa_results.json
```

To add more questions from a raw paste (question blocks with a final line "X. correct answer"), put the raw text in `scripts/data/aicpa_questions_raw.txt` and run:

```bash
python scripts/parse_aicpa_to_jsonl.py scripts/data/aicpa_questions_raw.txt >> scripts/data/aicpa_questions.jsonl
```

(Or overwrite by redirecting to the file instead of appending.)

## Differences: `/chat` vs `/test`

| Feature           | `POST /chat`           | `POST /test`                |
|------------------|------------------------|-----------------------------|
| User profile     | Required (or in body)   | Not required (default used) |
| Session          | Client sends session_id| New temp session per request|
| Use case         | Real user conversations| Batch / standardized tests  |

Use `/test` for automated or batch testing with a consistent, minimal profile. Use `/chat` for the normal app flow with real user profiles.
